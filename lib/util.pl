## 共通処理

use utf8;
use Encode;
use Encode::Guess;

sub parseInput
{
  my($encoding) = @_;
  my($method) = $ENV{'REQUEST_METHOD'};
  local($query, @in, $key, $val);
#  require 'jcode.pl' if $encoding;
  if ($method eq 'GET') {
    $query = $ENV{'QUERY_STRING'};
  }
  elsif ($method eq 'POST') {
    read(STDIN, $query, $ENV{'CONTENT_LENGTH'});
  }
  local(@query) = split(/&/, $query);
  foreach(@query) {  # $in{'Name'} = 'Val'
    tr/+/ /;
    ($key, $val) = split(/=/);
    $key =~ s/%([A-Fa-f0-9][A-Fa-f0-9])/pack("c", hex($1))/ge;
    $val =~ s/%([A-Fa-f0-9][A-Fa-f0-9])/pack("c", hex($1))/ge;
    $val == s/\r\n/\n/g;
#    jcode'convert(*key, $encoding) if ($encoding);
#    jcode'convert(*val, $encoding) if ($encoding);
    if( $encoding ) {
      my $guess;
#	  if( ! utf8::is_utf8($key) ) {
#        $guess = guess_encoding($key, qw/euc-jp shiftjis 7bit-jis/);
#        $key = encode('utf8', decode($guess, $key));
#        $guess = guess_encoding($key, qw/utf8 euc-jp cp932 7bit-jis/);
        $key = decode('UTF-8', $key);
#	  }
#	  if( ! utf8::is_utf8($val) ) {
#        $guess = guess_encoding($val, qw/euc-jp shiftjis 7bit-jis/);
#        $val = encode('utf8', decode($guess, $val));
#        $guess = guess_encoding($val, qw/utf8 euc-jp cp932 7bit-jis/);
        $val = decode('UTF-8', $val);
#	  }
    }
    $in{$key} = $val;
  }
  return *in;
}

sub error {
  my($message) = @_;

  print encode('utf-8', "エラーが発生しました<br>\n");
  if( length($message) > 0 ) {
    print encode('utf-8', "原因: ") . $message . "\n";
  }

  &tail();

  exit(1);
}

sub header {
  my($title) = @_;
  $title = encode('utf-8', $title) if(utf8::is_utf8($title));

  print "Content-Type: text/html\n\n";

if(isSP()) {
  # スマホ向けのHTMLヘッダ
  print <<EOF;
<!DOCTYPE html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width; initial-scale=1.0;">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<meta name="apple-touch-fullscreen" content="YES">
<meta http-equiv="Content-Script-Type" content="text/javascript">
<meta http-equiv="Content-Style-Type" content="text/css">
<!-- <meta name="apple-mobile-web-app-capable" content="yes"> -->
<!-- <meta name="apple-mobile-web-app-status-bar-style" content="black"> -->
<link rel="apple-touch-icon-precomposed" href="/oxygen-icons/categories/applications-internet.png">
EOF
} else {
  # PC向けヘッダ
  print <<EOF;
<!DOCTYPE html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta http-equiv="Content-Script-Type" content="text/javascript">
<meta http-equiv="Content-Style-Type" content="text/css">
EOF
}

print <<EOF;
<style type="text/css">
<!--
  .partition {
    clear: both;
    padding-top: 5px;
    padding-bottom: 5px;
   /* border-top: solid 1px; */
    margin: 5px 5px 0px 0px;
  }
  .listtext {
    margin-left: 10px;
    margin-right: 0px;
    margin-top: 3px;
    margin-bottom: 3px;
    font-weight: bold;
    font-size: 12pt;
  }
  a.content {
    /* text-decoration: none; */
  }
  div.imagebox {
    border: 1px dashed #0000cc;
    background-color: #eeeeff;
    float: left;
    margin: 5px;
  }
  p.image, p.caption {
    text-align: center;
    font-size: 75%;
    margin: 5px;
  }
  p.caption {
    color: darkblue;
  }
  table.tb1 {
    border: 1ps solid #666666;
    border-collapse: collapse;
    empty-cells: show;
    margin-top: 1em;
    margin-bottom: 1em;
    margin-left: 0em;
    margin-right: 0em;
  }
  table.tb1 th {
    font-size: 10pt;
    word-break: break-all;
    border: 1px solid #666666;
    padding: 0px 3px;
    background-color: #ccccff;
    color: #333366;
  }
  table.tb1 td {
    font-size: 10pt;
    word-break: break-all;
    border: 1px solid #666666;
    padding: 0px 3px;
  }
  table.center td {
    text-align: center;
    word-break: break-all;
  }
  table.tb1 caption {
    font-size: 10pt;
    text-align: left;
  }
  table.tb1 table th {
    border: 0px solid #666666;
  }
  table.tb1 table td {
    border: 0px solid #666666;
  }
-->
</style>
<title>${title}</title>
</head>
<body>
EOF

  return;
}

sub header_smp {
  my($title) = @_;
  $title = encode('utf-8', $title) if(utf8::is_utf8($title));

  print "Content-Type: text/html\n\n";
  print <<EOF;
<!DOCTYPE html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="viewport" content="width=device-width: initial-scale=1.0; maximum-scale=1.0; user-scalable=no;">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<meta name="apple-touch-fullscreen" content="YES">
<meta http-equiv="Content-Script-Type" content="text/javascript">
<meta http-equiv="Content-Style-Type" content="text/css">
<link rel="apple-touch-icon-precomposed" href="/oxygen-icons/categories/applications-internet.png">
<style type="text/css">
<!--
  body {
    font-size: 11pt;
  }

  div.center {
    text-align: center;
  }

  input.submit_button {
    background-color: #4169e1;
    color: #ffffff;
    font-family: Arial;
    border: 1px solid #ff9966;
    margin: 0px;
    padding: 5px 50px 5px 50px;
  }

  input.normal_button {
    background-color: #ffffff;
    color: #000000;
    font-family: Arial;
    border: 1px solid #ff9966;
    margin: 0px;
    padding: 5px 35px 5px 35px;
  }
-->
</style>
<title>${title}</title>
</head>
<body>
EOF

  return;
}

sub tail {
  print <<EOF;
</body>
</html>
EOF

  return;
}

sub isSP {
  # スマホチェック
  if(! $ENV{'HTTP_USER_AGENT'}) {
    # 不明な場合スマホ以外として扱う
    return 0;
  }

  my $agent = lc($ENV{'HTTP_USER_AGENT'});

  if(index($agent, "android") >=0 || index($agent, "mobile") >=0 ||
     index($agent, "ipod") >=0 || index($agent, "iphone") >=0  || index($agent, "ipad") >=0 )
  {
    return 1;
  }
  return 0;
}

sub escape_html {
  my($string) = @_;

  $string =~ s/&/&amp;/g;
  $string =~ s/"/&quot;/g;
  $string =~ s/</&lt;/g;
  $string =~ s/>/&gt;/g;

  $string =~ s/\r/&#x0d;/g;
  $string =~ s/\n/&#x0a;/g;

  return $string;
}

sub inode_path {
  my($path, $inodes) = @_;

  if($inodes =~ /[^0123456789\/]/) {
    return;
  }
  $inodes =~ s/^\///;

  foreach $inode (split('/', $inodes)) {
    my $match_flag = 0;
    opendir(DIR, $path) or return;
    while($entry = readdir DIR) {
      my $point_inode = (stat "$path/$entry")[1];
      if($inode == $point_inode) {
        $match_flag = 1;
        $path .= "/" . $entry;
        last;
      }
    }
    closedir(DIR);
    if($match_flag == 0) {
      return;
    }
  }

  return $path;
}

sub path_inode {
  my($path, $files) = @_;

  $files =~ s/^\///;
  my $all_inode = "";

  foreach $elem (split('/', $files)) {
    my $match_flag = 0;
    opendir(DIR, $path) or return;
    while($entry = readdir DIR) {
      if("$elem" eq "$entry") {
        my $point_inode = (stat "$path/$entry")[1];
        $match_flag = 1;
        $path .= "/" . $entry;
        $all_inode .= "/" . $point_inode;
        last;
      }
    }
    closedir(DIR);
    if($match_flag == 0) {
      return;
    }
  }

  return $all_inode;
}


__EXIT__

