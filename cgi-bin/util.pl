# Copyright 2016 suzutsuki0220
#     https://github.com/suzutsuki0220/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

use utf8;
use Encode;
use Encode::Guess;

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
<style type="text/css">
<!--
  body {
    font-size: 11pt;
  }

  div.center {
    text-align: center;
  }

  ul li {
    list-style: none;
  }

  ul {
    margin-left: 10px;
    padding-left: 0px;
  }

  input, select {
    border: 2px solid #d0d0d0;
    border-radius: 5px;
    font-size: 120%;
    margin: 3px 0px;
  }

  input[type="text"] {
    width: 375px;
  }

  label {
    width: 70px;
    float: left;
    margin: 3px 5px 3px 0px;
  }

  \@media screen and (max-width: 480px)
  {
    input[type="text"] {
      width: 77%;
    }

    label {
      width: 20%;
      float: left;
    }
  }

  input.submit_button {
    font-size: 100%;
    font-weight: bold;
    background-color: #4169e1;
    color: #ffffff;
    font-family: Arial;
    border: 1px solid #ff9966;
    margin: 0px;
    padding: 10px 50px 10px 50px;
  }

  input.normal_button {
    font-size: 100%;
    font-weight: bold;
    background-color: #ffffff;
    color: #000000;
    font-family: Arial;
    border: 1px solid #ff9966;
    margin: 0px;
    padding: 10px 35px 10px 35px;
  }

  #Calendar {
    background: -webkit-linear-gradient(top, #fff 0%, #f0f0f0 100%);
    background: linear-gradient(to bottom, #fff 0%, #f0f0f0 100%);
    border: 1px solid #ccc;
    border-top: 4px solid #1c66fe;
    box-shadow: 0 -1px 0 rgba(255, 255, 255, 1) inset;
    margin: 0.5em 0 2em 0;
    padding: 2em;
    width: 200px;
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

sub escape_wquot {
  my($string) = @_;

  $string =~ s/"/\\"/g;

  return $string;
}

__EXIT__

