#!/usr/bin/perl

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
use Encode::JP;
use Encode::Guess;
use DBI;
use CGI;

# This script need MySQL database
# To make required database, please run this command below.
# ---
#  # mysql -u root -p
#  mysql> CREATE DATABASE suitou;
#  mysql>CREATE TABLE suitou.webform (
#      -> id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
#      -> year INT NOT NULL,
#      -> month INT NOT NULL,
#      -> day INT NOT NULL,
#      -> category VARCHAR(16) NOT NULL,
#      -> summary VARCHAR(512) NOT NULL,
#      -> expend MEDIUMINT UNSIGNED DEFAULT 0 NOT NULL,
#      -> income MEDIUMINT UNSIGNED DEFAULT 0 NOT NULL,
#      -> note VARCHAR(512) );
#  mysql> GRANT SELECT,UPDATE,INSERT,DELETE ON suitou.* TO mysql@localhost IDENTIFIED BY 'mysql';
#  mysql> CREATE INDEX idx_year_mon ON webform (year, month);
#  mysql> CREATE INDEX idx_year ON webform (year);
#  mysql> CREATE INDEX idx_month ON webform (month);
#
# ---
require './util.pl';

my $db_user = "mysql";
my $db_pass = "mysql";
my $db_host = "localhost";
my $db_name = "suitou";
my @db_opt  = {RaiseError => 1, mysql_enable_utf8 => 1};

my $form = eval{new CGI};

# 分類
my @category = (
"食費",
"外食",
"交通費",
"生活品",
"娯楽",
"交際費",
"衣料品",
"医療費",
"光熱費",
"通信費",
"家賃",
"保険",
"手数料",
"金融",
"収入",
"その他"
);

my $mode = scalar($form->param('mode'));

if( $mode eq '' || $mode eq 'reg') {
  &print_input_form();
} elsif( $mode eq 'confirm_input' ) {
  &confirm_input();
} elsif( $mode eq 'do_input' ) {
  &do_input();
} elsif( $mode eq 'view' ) {
  &print_view_form();
} elsif( $mode eq 'figures' ) {
  &print_figures();
} elsif( $mode eq 'edit' ) {
  &print_edit_form();
} elsif( $mode eq 'do_edit' ) {
  &do_edit();
} elsif( $mode eq 'do_delete' ) {
  &do_delete();
#} elsif( $mode eq 'memo_edit' ) {
#  &print_memoedit_form();
} elsif( $mode eq 'memo_do_edit' ) {
  &do_memoedit();
} elsif( $mode eq 'csv' ) {
  &csv();
} elsif( $mode eq 'restore' ) {
  &restore_form();
} elsif( $mode eq 'do_restore' ) {
  &data_restore();
} elsif( $mode eq 'count' ) {
  &data_count();
} else {
  &print_input_form();
}

exit(0);

##############
#  入力画面  #
##############
sub print_input_form {
  my $q_date     = &escape_html(decode('utf-8', scalar($form->param('date'))));
  my $q_category = &escape_html(decode('utf-8', scalar($form->param('category'))));
  my $q_summary  = &escape_html(decode('utf-8', scalar($form->param('summary'))));
  my $q_expend   = &escape_html(decode('utf-8', scalar($form->param('expend'))));
  my $q_income   = &escape_html(decode('utf-8', scalar($form->param('income'))));
  my $q_note     = &escape_html(decode('utf-8', scalar($form->param('note'))));

  my($q_year, $q_mon, $q_day) = split(/[\/\-]/, $q_date);

  my($sec, $min, $hour, $day, $mon, $year) = localtime(time);
  $year += 1900;
  $mon += 1;

  if (! $q_date || $q_date eq '') {
    $q_date = "${year}/${mon}/${day}";
    $q_year = $year;
    $q_mon  = $mon;
    $q_day  = $day;
  }

  &header_smp(encode('utf-8', '出納入力画面'));

  my $mes = <<EOF;
<script type="text/JavaScript">
<!--
  function check_inform() {
    document.f_input.date.value = zenkaku2hankaku(document.f_input.date.value);
    document.f_input.summary.value = zenkaku2hankaku(document.f_input.summary.value);
    document.f_input.expend.value = zenkaku2hankaku(document.f_input.expend.value);
    document.f_input.income.value = zenkaku2hankaku(document.f_input.income.value);
    document.f_input.note.value = zenkaku2hankaku(document.f_input.note.value);

    document.f_input.date.value = document.f_input.date.value.replace(/ +\$/, "");
    document.f_input.date.value = document.f_input.date.value.replace(/^ +/, "");
    document.f_input.summary.value = document.f_input.summary.value.replace(/ +\$/, "");
    document.f_input.summary.value = document.f_input.summary.value.replace(/^ +/, "");
    document.f_input.expend.value = document.f_input.expend.value.replace(/ +\$/, "");
    document.f_input.expend.value = document.f_input.expend.value.replace(/^ +/, "");
    document.f_input.income.value = document.f_input.income.value.replace(/ +\$/, "");
    document.f_input.income.value = document.f_input.income.value.replace(/^ +/, "");
    document.f_input.note.value = document.f_input.note.value.replace(/ +\$/, "");
    document.f_input.note.value = document.f_input.note.value.replace(/^ +/, "");

    ymh = document.f_input.date.value.split("/");
    if(ymh[0].length == 0 || ymh[0] > 2099 || ymh[0] < 2000) {
      alert('年が正しくありません');
      return false;
    }
    if(ymh[1].length == 0 || ymh[1] > 12 || ymh[1] < 1) {
      alert('月が正しくありません');
      return false;
    }
    if(ymh[2].length == 0 || ymh[2] > 31 || ymh[2] < 1) {
      alert('日が正しくありません');
      return false;
    }
    if(ymh[0] < ${year}) {
      if( ! window.confirm('年が過去ですが、よろしいですか？')) {
        return false;
      }
    }
    if(ymh[0] > ${year}) {
      if( ! window.confirm('年が未来ですが、よろしいですか？')) {
        return false;
      }
    }
    if(ymh[0] == ${year} && ymh[1] > ${mon}) {
      if( ! window.confirm('未来の月ですが、よろしいですか？')) {
        return false;
      }
    }
    if(ymh[0] == ${year} && ymh[1] < ${mon}) {
      if( ! window.confirm('過去の月ですが、よろしいですか？')) {
        return false;
      }
    }
    if(! document.f_input.expend.value || document.f_input.expend.value <= 0) {
      document.f_input.expend.value = 0;
    }
    if(! document.f_input.income.value || document.f_input.income.value <= 0) {
      document.f_input.income.value = 0;
    }
    if(document.f_input.income.value == 0 && document.f_input.expend.value == 0) {
      alert('支出と収入が共に0になってます');
      return false;
    }
    if(document.f_input.date.value.match(/[^0-9/]+/)) {
      alert('月／日に数字以外の文字が含まれています');
      return false;
    }
    if(document.f_input.expend.value.match(/[^0-9]+/)) {
      alert('支出に数字以外の文字が含まれています');
      return false;
    }
    if(document.f_input.income.value.match(/[^0-9]+/)) {
      alert('収入に数字以外の文字が含まれています');
      return false;
    }
    if(! document.f_input.category.value) {
      alert('分類を選択してください');
      return false;
    }
    if(! document.f_input.date.value) {
      alert('日付を入れてください');
      return false;
    }
    if(! document.f_input.summary.value) {
      alert('摘要を入れてください');
      return false;
    }
    return true;
  }

  function zenkaku2hankaku(s) {
    s = s.replace(/[Ａ-Ｚａ-ｚ０-９／]/g, function(s) {
      return String.fromCharCode(s.charCodeAt(0) - 0xFEE0);
    });
    s = s.replace(/　/g, " ");
    return s;
  }
-->
</script>

<h2>出納入力画面</h2>
<form action="$ENV{'SCRIPT_NAME'}" name="f_input" onSubmit="return check_inform()" method="post">
<input type="hidden" name="mode" value="confirm_input">
<tt>月／日　</tt>
<input type="text" name="date" size="20" tabindex="1" autocomplete="off"><br>
<tt>分類　　</tt>
<select name="category" tabindex="2">
<option value="">--</option>
EOF
  print encode('utf-8', $mes);
  foreach $item (@category) {
    print "<option>" . encode('utf-8', $item) . "</option>";
  }
  $mes = <<EOF;
</select><br>
<tt>摘要　　</tt>
<input type="text" name="summary" size="25" maxlength="512" tabindex="3" autofocus autocomplete="off"><br>
<tt>支出金額</tt>
<input type="number" name="expend" size="10" tabindex="4" onChange="hankaku_expend()" autocomplete="off"><br>
<tt>収入金額</tt>
<input type="number" name="income" size="10" tabindex="5" autocomplete="off"><br>
<tt>備考　　</tt>
<input type="text" name="note" size="25" maxlength="512" tabindex="6" autocomplete="off"><br><br>
<div class="center"><input type="submit" class="submit_button" name="b_submit" tabindex="7" value="送信"></div><br>
</form>
<hr>
<a href="$ENV{'SCRIPT_NAME'}?mode=view&year=${q_year}&mon=${q_mon}">出納出力</a> | 
<a href="$ENV{'SCRIPT_NAME'}?mode=figures&year=${q_year}&mon=${q_mon}">統計画面</a>
<script type="text/javascript">
<!--
  document.f_input.date.value = "$q_date";
  document.f_input.category.value = "$q_category";
  document.f_input.summary.value = "$q_summary";
  document.f_input.expend.value = "$q_expend";
  document.f_input.income.value = "$q_income";
  document.f_input.note.value = "$q_note";
-->
</script>
EOF
  print encode('utf-8', $mes);

  &tail();
  exit(0);
}

sub confirm_input {
  my $q_date     = &escape_html(decode('utf-8', scalar($form->param('date'))));
  my $q_category = &escape_html(decode('utf-8', scalar($form->param('category'))));
  my $q_summary  = &escape_html(decode('utf-8', scalar($form->param('summary'))));
  my $q_expend   = &escape_html(decode('utf-8', scalar($form->param('expend'))));
  my $q_income   = &escape_html(decode('utf-8', scalar($form->param('income'))));
  my $q_note     = &escape_html(decode('utf-8', scalar($form->param('note'))));

  &header_smp(encode('utf-8', '確認画面'));

  my $mes = <<EOF;
<script type="text/javascript">
<!--
  function disable_button() {
    document.f_input.b_submit.disabled = true;
    document.f_input.b_back.disabled = true;
  }

  function back_input() {
    document.f_input.mode.value = "reg";
    document.f_input.submit();
  }
-->
</script>
<h2>確認画面</h2>
<p>この内容で登録します。</p>
<form action="$ENV{'SCRIPT_NAME'}" name="f_input" method="post" onSubmit="disable_button()">
<input type="hidden" name="mode" value="do_input">
<tt>月／日　</tt>
<input type="text" name="date" size="20" value="$q_date" readonly><br>
<tt>分類　　</tt>
<input type="text" name="category" size="10" value="$q_category" readonly><br>
<tt>摘要　　</tt>
<input type="text" name="summary" size="25" value="$q_summary" readonly><br>
<tt>支出金額</tt>
<input type="text" name="expend" size="10" value="$q_expend" readonly><br>
<tt>収入金額</tt>
<input type="text" name="income" size="10" value="$q_income" readonly><br>
<tt>備考　　</tt>
<input type="text" name="note" size="25" value="$q_note" readonly><br><br>
<div class="center">
<input type="submit" class="submit_button" name="b_submit" value="登録">&nbsp;
<input type="button" class="normal_button" onClick="back_input()" name="b_back" value="戻る">
</div><br>
</form>
EOF
  print(encode('utf-8', $mes));
  &tail();
  exit(0);
}

sub do_input {
  &header_smp(encode('utf-8', '登録しました'));

  my $dbh = DBI->connect("DBI:mysql:$db_name@$db_host", $db_user, $db_pass, @db_opt);

  my $q_date     = &escape_html(decode('utf-8', scalar($form->param('date'))));
  my $q_category = $dbh->quote(decode('utf-8', scalar($form->param('category'))));
  my $q_summary  = $dbh->quote(decode('utf-8', scalar($form->param('summary'))));
  my $q_expend   = int(scalar($form->param('expend')));
  my $q_income   = int(scalar($form->param('income')));
  my $q_note     = $dbh->quote(decode('utf-8', scalar($form->param('note'))));
  my $q_user     = $dbh->quote($ENV{'REMOTE_USER'});

  my($year, $mon, $day) = split(/[\/\-]/, $q_date);

  # 入力値チェック
  if($year !~ /^\d+$/ || $year < 2000 || $year > 2050 ||
     $mon  !~ /^\d+$/ || $mon  < 0    || $mon  > 13   ||
     $day  !~ /^\d+$/ || $day  < 0    || $day  > 32 )
  {
    &error(encode('utf-8', "月／日が不正です。"));
  }
  if($q_category eq "''") {
    &error(encode('utf-8', "分類が入っていません。"));
  }
  if($q_expend !~ /^\d+$/ || $q_expend < 0 || $q_expend > 1000000) {
    &error(encode('utf-8', "支出が不正です。"));
  }
  if($q_income !~ /^\d+$/ || $q_income < 0 || $q_income > 1000000) {
    &error(encode('utf-8', "収入が不正です。"));
  }

  my $query = "INSERT INTO webform (year, month, day, category, summary, expend, income, note, user) ";
  $query .= "VALUES ($year, $mon, $day, $q_category, $q_summary, $q_expend, $q_income, $q_note, $q_user);";

  eval {
    my $sth = $dbh->prepare($query);
    $sth->execute();
    $sth->finish();
  };

  if($@) {
    &error(encode('utf-8', "登録に失敗しました"));
  }

  $dbh->disconnect;

  my $mes = <<EOF;
<h2>登録しました。</h2>
<form action="$ENV{'SCRIPT_NAME'}" name="f" method="POST">
<div class="center">
<input type="hidden" name="mode" value="reg">
<input type="hidden" name="year" value="${year}">
<input type="hidden" name="mon"  value="${mon}">
<input type="submit" class="normal_button" style="width: 160px; margin-bottom: 5px;" value="入力画面に戻る"><br>
<input type="button" class="normal_button" style="width: 160px; margin-top: 5px" onClick="gotoView()" value="出納を見る">
</div>
</form>
<script type="text/javascript">
<!--
function gotoView() {
  document.f.mode.value = "view";
  document.f.submit();
}
-->
</script>
EOF
  print(encode('utf-8', $mes));
  &tail();
  exit(0);
}


##############
#  出力画面  #
##############
sub print_view_form() {
  &header(encode('utf-8', '出納出力'));
  my $dbh = DBI->connect("DBI:mysql:$db_name@$db_host", $db_user, $db_pass, @db_opt);

  my($sec, $min, $hour, $day, $mon, $year) = localtime(time);
  $year += 1900;
  $mon += 1;
  $year = &escape_html(scalar $form->param('year')) if length(scalar $form->param('year')) > 0;
  $mon = &escape_html(scalar $form->param('mon')) if length(scalar $form->param('mon')) > 0;

  my $mes = <<EOF;
<span style="float: left">
<a href="$ENV{'SCRIPT_NAME'}">入力画面</a> | <a href="$ENV{'SCRIPT_NAME'}?mode=figures&year=${year}&mon=${mon}">統計画面</a>
</span><span style="float: right">
<a href="$ENV{'SCRIPT_NAME'}?mode=csv&year=${year}&mon=${mon}">CSV出力</a>
</span>
<br><hr>
<h2>${year}年${mon}月の出納</h2>
EOF
  print(encode('utf-8', $mes));

  my $query;
  my $expend = 0;
  my $income = 0;
  my $remain = 0;
  $query  = "SELECT sum(expend), sum(income) ";
  $query .= "FROM webform WHERE year = ${year} AND month = ${mon};";
  my $sth = $dbh->prepare($query);
  $sth->execute();
  if ($sth->rows > 0) {
    my @row = $sth->fetchrow_array;
    $expend = $row[0] if defined $row[0];
    $income = $row[1] if defined $row[0];
  }
  $sth->finish();

  $remain = int($income) - int($expend);
  1 while $expend =~ s/(\d)(\d\d\d)(?!\d)/$1,$2/g;
  1 while $income =~ s/(\d)(\d\d\d)(?!\d)/$1,$2/g;
  1 while $remain =~ s/(\d)(\d\d\d)(?!\d)/$1,$2/g;

  $mes = <<EOF;
<script type="text/javascript">
<!--
  function isNumber(x){ 
    if(typeof(x) != 'number' && typeof(x) != 'string')
      return false;
    else 
      return (x == parseFloat(x) && isFinite(x));
  }

  function ymchange() {
    if(isNumber(document.fym.year.value) == false) {
      alert("年を修正してください");
      return;
    }

    if(document.fym.year.value < 2000 || document.fym.year.value > 2031) {
      return;
    }
    document.fym.submit();
  }
-->
</script>
<div style="width: 700px; text-align: right;">
<span style="float: left"><br>
<form action="$ENV{'SCRIPT_NAME'}" method="GET" name="fym">
<input type="hidden" name="mode" value="view">
年／月: <input type="text" name="year" size="6" value="$year" onChange="ymchange()">年
<select name="mon" size="1" onChange="ymchange()">
EOF
  print(encode('utf-8', $mes));

  for($i=1;$i<=12;$i++) {
    if($i==$mon) {
      print "<option selected>$i</option>";
    } else {
      print "<option>$i</option>";
    }
  }
  $mes = <<EOF;
</select>月
</form></span>
<span style="float: right">
<table class="tb1" style="margin-left: auto; margin-right: 0px">
<tr><th width="80">支出合計</th><th width="80">収入合計</th><th width="80">差引</th></tr>
<tr><td>￥${expend}</td><td>￥${income}</td><td>
EOF
  print(encode('utf-8', $mes));
  if($remain < 0) {
    print "<span style=\"color: #ff0000\">";
    print(encode('utf-8', "￥${remain}</span>"));
  } else {
    print(encode('utf-8', "￥${remain}"));
  }

  # メモ欄
  my $memo_text;
  $query  = "SELECT text ";
  $query .= "FROM memo WHERE year = ${year} AND month = ${mon};";
  $sth = $dbh->prepare($query);
  $sth->execute();
  if ($sth->rows > 0) {
    my @row = $sth->fetchrow_array;
    $memo_text = $row[0] if defined $row[0];
  }
  my $memo_value = $memo_text;
  $memo_value =~ s/&#x0d;&#x0a;/\\n/g;
  $mes = <<EOF;
</td></tr>
</table></span></div>
<script type="text/javascript">
<!--
function confirmEditMemo() {
  if(confirm("メモを編集しますか?")) {
    document.memo_top.mode.value = "memo_edit";
    document.memo_top.submit();
  }
}
function showMemoButton() {
  document.memo_top.memo.readOnly = false;
  htmldata  = '<input type="submit" value="保存">&nbsp;';
  htmldata += '<input type="button" onClick="hideMemoButton()" value="キャンセル">';
  document.getElementById('MemoButton').innerHTML = htmldata;
}
function hideMemoButton() {
  document.memo_top.memo.readOnly = true;
  document.memo_top.memo.value = '${memo_value}';
  document.getElementById('MemoButton').innerHTML = '';
}
-->
</script>
<p style="clear: both"></p>
<form action="$ENV{'SCRIPT_NAME'}" method="POST" name="memo_top">
<input type="hidden" name="mode" value="memo_do_edit">
<input type="hidden" name="year" value="${year}">
<input type="hidden" name="mon" value="${mon}">
<textarea rows="3" readonly name="memo" style="width: 700px; height: 45px; font-size: 9pt; resize:none" onClick="showMemoButton()">${memo_text}</textarea>
<div style="text-align: right; width: 700px" id="MemoButton"></div>
</form>
EOF
  print(encode('utf-8', $mes));

  $query  = "SELECT year, month, day, category, summary, expend, income, note, id ";
  $query .= "FROM webform WHERE year = ${year} AND month = ${mon} ORDER BY day ASC;";
  $sth = $dbh->prepare($query);
  $sth->execute();
  if ($sth->rows <= 0) {
    print(encode('utf-8', "<p>出納は登録されていません。</p>\n"));
  } else {
    $mes = <<EOF;
<table class="tb1" width="700">
<tr>
<th width="90">月／日</th>
<th width="60">分類</th>
<th width="230">摘要</th>
<th width="70">支出金額</th>
<th width="70" style="text-align: right;">収入金額</th>
<th width="180">備考</th></tr>
EOF
    print(encode('utf-8', $mes));
    while(@row = $sth->fetchrow_array) {
      print "<tr>\n";
      for( my $i=0; $i<@row.length; $i++ ) {
        $row[$i] = &escape_html($row[$i]);
        $row[$i] = '&nbsp;' unless (defined $row[$i]);
        $row[$i] = '&nbsp;' if ($row[$i] eq "");
        $row[$i] = '&nbsp;' if ($row[$i] eq "0");
      }
      1 while $row[5] =~ s/(\d)(\d\d\d)(?!\d)/$1,$2/g;
      1 while $row[6] =~ s/(\d)(\d\d\d)(?!\d)/$1,$2/g;
      print "<td style=\"text-align: center;\">$row[0]/$row[1]/$row[2]</td>\n";
      print "<td style=\"text-align: center;\">".encode('utf-8', $row[3])."</td>\n";
      print "<td><a href=\"$ENV{SCRIPT_NAME}?mode=edit&id=$row[8]\">";
      print encode('utf-8', $row[4])."</a></td>\n";
      print "<td style=\"text-align: right;\">$row[5]</td>\n";
      print "<td style=\"text-align: right;\">$row[6]</td>\n";
      print "<td>".encode('utf-8', $row[7])."</td>\n";
      print "</tr>\n";
    }
    print "</table>\n";
  }

  $sth->finish();
  $dbh->disconnect;

  &tail();
  exit(0);
}

sub print_figures {
  &header(encode('utf-8', '統計情報'));
  my $dbh = DBI->connect("DBI:mysql:$db_name@$db_host", $db_user, $db_pass, @db_opt);

  my($sec, $min, $hour, $day, $mon, $year) = localtime(time);
  $year += 1900;
  $mon += 1;
  $year = &escape_html(scalar $form->param('year')) if length(scalar $form->param('year')) > 0;
  $mon = &escape_html(scalar $form->param('mon')) if length(scalar $form->param('mon')) > 0;

  my $mes = <<EOF;
<a href="$ENV{'SCRIPT_NAME'}">入力画面</a> | <a href="$ENV{'SCRIPT_NAME'}?mode=view&year=${year}&mon=${mon}">出納出力</a>
<hr>
<h2>${year}年${mon}月の統計</h2>
<form action="$ENV{'SCRIPT_NAME'}" method="GET" name="fym">
<input type="hidden" name="mode" value="figures">
年／月: <input type="text" name="year" size="6" value="$year" onChange="ymchange()">年 
<select name="mon" size="1" onChange="ymchange()">
EOF
  print(encode('utf-8', $mes));
  for($i=1;$i<=12;$i++) {
    if($i==$mon) {
      print "<option selected>$i</option>";
    } else {
      print "<option>$i</option>";
    }
  }
  $mes = <<EOF;
</select>月
</form>
<script type="text/javascript">
<!--
  function isNumber(x){ 
    if(typeof(x) != 'number' && typeof(x) != 'string')
      return false;
    else 
      return (x == parseFloat(x) && isFinite(x));
  }

  function ymchange() {
    if(isNumber(document.fym.year.value) == false) {
      alert("年を修正してください");
      return;
    }

    if(document.fym.year.value < 2000 || document.fym.year.value > 2031) {
      return;
    }
    document.fym.submit();
  }
-->
</script>
<h3>日毎の支出</h3>
<table class="tb1">
<tr><th>日</th><th>支出</th><th>収入</th><th>差引</th></tr>
EOF
  print(encode('utf-8', $mes));

  my $i;
  my $balance = 0;
  my $total_expend = 0;
  my $total_income = 0;
  for($i=1;$i<=31;$i++) {
    my $query;
    my $expend = 0;
    my $income = 0;
    $query  = "SELECT sum(expend), sum(income) FROM webform WHERE ";
    $query .= "year = ${year} AND month = ${mon} AND day = ${i};";
    my $sth = $dbh->prepare($query);
    $sth->execute();
    if ($sth->rows > 0) {
      my @row = $sth->fetchrow_array;
      $expend = $row[0] if defined $row[0];
      $income = $row[1] if defined $row[1];
    }
    $total_expend += $expend;
    $total_income += $income;
    $balance = $total_income - $total_expend;
    1 while $expend =~ s/(\d)(\d\d\d)(?!\d)/$1,$2/g;
    1 while $income =~ s/(\d)(\d\d\d)(?!\d)/$1,$2/g;
    1 while $balance =~ s/(\d)(\d\d\d)(?!\d)/$1,$2/g;
    print "<tr><td style=\"width: 60px; text-align: center\">${i}</td><td style=\"width: 70px; text-align: right\">${expend}</td><td style=\"width: 70px; text-align: right\">${income}</td><td style=\"width: 70px; text-align: right\">${balance}</tr>\n";
  }
  1 while $total_expend =~ s/(\d)(\d\d\d)(?!\d)/$1,$2/g;
  1 while $total_income =~ s/(\d)(\d\d\d)(?!\d)/$1,$2/g;
  $mes = <<EOF;
<tr><th>合計</th><td style="width: 70px; text-align: right">$total_expend</td><td style="width: 70px; text-align: right">$total_income</td><td style="width: 70px; text-align: right">$balance</td></tr>
</table>
<h3>分類別の合計</h3>
<table class="tb1">
<tr><td>&nbsp;</td>
EOF
  print(encode('utf-8', $mes));
  for($i=1;$i<=12;$i++) {
    if($i==$mon) {
      print(encode('utf-8', "<th>今月</th>"));
    } else {
      print(encode('utf-8', "<th>${i}月</th>"));
    }
  }
  print "</tr>\n";
  foreach $key (@category) {
    if($key eq "収入") {
      next;
    }
    print "<tr><th style=\"width: 60px; text-align: center\">";
    print(encode('utf-8', "${key}</th>"));
    for($i=1;$i<=12;$i++) {
      my $query;
      my $expend = 0;
      $query  = "SELECT sum(expend) FROM webform WHERE ";
      $query .= "category = '${key}' AND year = ${year} AND month = ${i};";
      $sth = $dbh->prepare($query);
      $sth->execute();
      if ($sth->rows > 0) {
        my @row = $sth->fetchrow_array;
        $expend = $row[0] if defined $row[0];
      }
      1 while $expend =~ s/(\d)(\d\d\d)(?!\d)/$1,$2/g;
      print "<td style=\"width: 70px; text-align: right\">${expend}</td>";
    }
    print "</tr>\n";
  }
  print "</table>\n";

  $sth->finish();
  $dbh->disconnect;

  &tail();
  exit(0);
}

sub print_edit_form {
  &header_smp(encode('utf-8', '編集'));

  if(! scalar($form->param('id')) || scalar($form->param('id')) eq '') {
    &error(encode('utf-8', 'IDが指定されていません'));
  } 

  my $id = &escape_html(scalar $form->param('id'));
  my $dbh = DBI->connect("DBI:mysql:$db_name@$db_host", $db_user, $db_pass, @db_opt);

  my $query  = "SELECT year, month, day, category, summary, expend, income, note ";
     $query .= "FROM webform WHERE id=${id};";

  my $sth = $dbh->prepare($query);
  $sth->execute();
  if ($sth->rows > 0) {
    my @row = $sth->fetchrow_array;
    my $q_date     = &escape_html("$row[0]/$row[1]/$row[2]");
    my $q_category = &escape_html($row[3]);
    my $q_summary  = &escape_html($row[4]);
    my $q_expend   = &escape_html($row[5]);
    my $q_income   = &escape_html($row[6]);
    my $q_note     = &escape_html($row[7]);

    my $mes = <<EOF;
<h2>出納編集画面</h2>
<form action="$ENV{'SCRIPT_NAME'}" name="f_input" onSubmit="return check_inform()" method="post">
<input type="hidden" name="mode" value="do_edit">
<input type="hidden" name="id" value="$id">
<tt>月／日　</tt>
<input type="text" name="date" size="20" tabindex="1" value="${q_date}" autocomplete="off"><br>
<tt>分類　　</tt>
<select name="category" tabindex="2">
EOF
  print(encode('utf-8', $mes));
  foreach $item (@category) {
    print(encode('utf-8', "<option>$item</option>"));
  }
  $mes = <<EOF;
</select><br>
<tt>摘要　　</tt>
<input type="text" name="summary" size="25" maxlength="512" tabindex="3" autofocus autocomplete="off"><br>
<tt>支出金額</tt>
<input type="number" name="expend" size="10" tabindex="4" autocomplete="off"><br>
<tt>収入金額</tt>
<input type="number" name="income" size="10" tabindex="5" autocomplete="off"><br>
<tt>備考　　</tt>
<input type="text" name="note" size="25" maxlength="512" tabindex="6" autocomplete="off"><br><br>
※項目を削除するには全ての欄を空にしてください<br>
<div class="center"><input type="submit" class="submit_button" name="b_submit" tabindex="7" value="送信">&nbsp;
<input type="button" class="normal_button" onClick="back_input()" name="b_back" tabindex="8" value="戻る">
</div><br>
</form>

<script type="text/JavaScript">
<!--
  document.f_input.date.value = "${q_date}";
  document.f_input.category.value = "${q_category}";
  document.f_input.summary.value = "${q_summary}";
  document.f_input.expend.value = "${q_expend}";
  document.f_input.income.value = "${q_income}";
  document.f_input.note.value = "${q_note}";

  function check_inform() {
    if(! document.f_input.expend.value && ! document.f_input.income.value &&
        ! document.f_input.date.value && ! document.f_input.summary.value )
    {
      if( confirm("この項目を削除してよろしいですか?")) {
        document.f_input.mode.value = "do_delete";
        document.f_input.b_submit.disabled = true;
        document.f_input.b_back.disabled = true;
        document.f_input.submit();
        return true;
      } else {
        return false;
      }
    }
 
    document.f_input.date.value = zenkaku2hankaku(document.f_input.date.value);
    document.f_input.summary.value = zenkaku2hankaku(document.f_input.summary.value);
    document.f_input.expend.value = zenkaku2hankaku(document.f_input.expend.value);
    document.f_input.income.value = zenkaku2hankaku(document.f_input.income.value);
    document.f_input.note.value = zenkaku2hankaku(document.f_input.note.value);

    document.f_input.date.value = document.f_input.date.value.replace(/ +\$/, "");
    document.f_input.date.value = document.f_input.date.value.replace(/^ +/, "");
    document.f_input.summary.value = document.f_input.summary.value.replace(/ +\$/, "");
    document.f_input.summary.value = document.f_input.summary.value.replace(/^ +/, "");
    document.f_input.expend.value = document.f_input.expend.value.replace(/ +\$/, "");
    document.f_input.expend.value = document.f_input.expend.value.replace(/^ +/, "");
    document.f_input.income.value = document.f_input.income.value.replace(/ +\$/, "");
    document.f_input.income.value = document.f_input.income.value.replace(/^ +/, "");
    document.f_input.note.value = document.f_input.note.value.replace(/ +\$/, "");
    document.f_input.note.value = document.f_input.note.value.replace(/^ +/, "");

    ymh = document.f_input.date.value.split("/");
    if(ymh[0].length == 0 || ymh[0] > 2099 || ymh[0] < 2000) {
      alert('年が正しくありません');
      return false;
    }
    if(ymh[1].length == 0 || ymh[1] > 12 || ymh[1] < 1) {
      alert('月が正しくありません');
      return false;
    }
    if(ymh[2].length == 0 || ymh[2] > 31 || ymh[2] < 1) {
      alert('日が正しくありません');
      return false;
    }
    if(! document.f_input.expend.value || document.f_input.expend.value <= 0) {
      document.f_input.expend.value = 0;
    }
    if(! document.f_input.income.value || document.f_input.income.value <= 0) {
      document.f_input.income.value = 0;
    }
    if(document.f_input.income.value == 0 && document.f_input.expend.value == 0) {
      alert('支出と収入が共に0になってます');
      return false;
    }
    if(! document.f_input.category.value) {
      alert('分類を選択してください');
      return false;
    }
    if(! document.f_input.date.value) {
      alert('日付を入れてください');
      return false;
    }
    if(! document.f_input.summary.value) {
      alert('摘要を入れてください');
      return false;
    }

    disable_button();
    return true;
  }

  function zenkaku2hankaku(s) {
    s = s.replace(/[Ａ-Ｚａ-ｚ０-９／]/g, function(s) {
      return String.fromCharCode(s.charCodeAt(0) - 0xFEE0);
    });
    s = s.replace(/　/g, " ");
    return s;
  }

  function disable_button() {
    document.f_input.b_submit.disabled = true;
    document.f_input.b_back.disabled = true;
  }

  function back_input() {
    document.f_input.mode.value = "view";
    document.f_input.submit();
  }
-->
</script>
EOF
    print(encode('utf-8', $mes));
  } else {
    &error(encode('utf-8', 'データが見つかりませんでした'));
  }
  $sth->finish();

  $dbh->disconnect;

  &tail();
  exit(0);
}

sub do_edit {
  &header_smp(encode('utf-8', '編集しました'));

  if(! scalar($form->param('id')) || scalar($form->param('id')) eq '') {
    &error(encode('utf-8', 'IDが指定されていません'));
  } 

  my $dbh = DBI->connect("DBI:mysql:$db_name@$db_host", $db_user, $db_pass, @db_opt);

  my $q_id       = int(scalar $form->param('id'));
  my $q_date     = &escape_html(scalar $form->param('date'));
  my $q_category = $dbh->quote(scalar $form->param('category'));
  my $q_summary  = $dbh->quote(scalar $form->param('summary'));
  my $q_expend   = int(scalar $form->param('expend'));
  my $q_income   = int(scalar $form->param('income'));
  my $q_note     = $dbh->quote(scalar $form->param('note'));

  my($year, $mon, $day) = split(/[\/\-]/, $q_date);
  # 入力値チェック
  if($year !~ /^\d+$/ || $year < 2000 || $year > 2050 ||
     $mon  !~ /^\d+$/ || $mon  < 0    || $mon  > 13   ||
     $day  !~ /^\d+$/  || $day  < 0    || $day  > 32 )
  {
    &error(encode('utf-8', "月／日が不正です。"));
  }
  if($q_category eq "''") {
    &error(encode('utf-8', "分類が入っていません。"));
  }
  if($q_expend !~ /^\d+$/ || $q_expend < 0 || $q_expend > 1000000) {
    &error(encode('utf-8', "支出が不正です。"));
  }
  if($q_income !~ /^\d+$/ || $q_income < 0 || $q_income > 1000000) {
    &error(encode('utf-8', "収入が不正です。"));
  }

  my $query = "UPDATE webform SET year=$year, month=$mon, day=$day, category=$q_category, summary=$q_summary, ";
  $query .= "expend=$q_expend, income=$q_income, note=$q_note WHERE id=$q_id;";

  eval {
    my $sth = $dbh->prepare($query);
    $sth->execute();
    $sth->finish();
  };

  if($@) {
    &error(encode('utf-8', "データベースにエラーが発生しました"));
  }

  $dbh->disconnect;

  my $mes = <<EOF;
<h2>編集しました。</h2>
<form action="$ENV{'SCRIPT_NAME'}" name="f" method="POST">
<div class="center">
<input type="hidden" name="mode" value="view">
<input type="hidden" name="year" value="${year}">
<input type="hidden" name="mon"  value="${mon}">
<input type="submit" class="normal_button" value="出納出力に戻る">
</div>
</form>
EOF
  print(encode('utf-8', $mes));

  &tail();
  exit(0);
}

sub do_delete {
  &header_smp(encode('utf-8', '削除しました'));

  if(! scalar($form->param('id')) || scalar($form->param('id')) eq '') {
    &error('IDが指定されていません');
  } 

  my $dbh = DBI->connect("DBI:mysql:$db_name@$db_host", $db_user, $db_pass, @db_opt);
  my $q_id = int(scalar $form->param('id'));

  my $query = "DELETE FROM webform WHERE id=$q_id;";
  eval {
    my $sth = $dbh->prepare($query);
    $sth->execute();
    $sth->finish();
  };

  if($@) {
    &error("データベースにエラーが発生しました");
  }

  $dbh->disconnect;

  my $mes = <<EOF;
<h2>削除しました。</h2>
<form action="$ENV{'SCRIPT_NAME'}" name="f" method="POST">
<div class="center">
<input type="hidden" name="mode" value="view">
<input type="submit" class="normal_button" value="出納出力に戻る">
</div>
</form>
EOF
  print(encode('utf-8', $mes));

  &tail();
  exit(0);
}

sub print_memoedit_form() {
  my $dbh = DBI->connect("DBI:mysql:$db_name@$db_host", $db_user, $db_pass, @db_opt);
  my ($q_year) = int(scalar $form->param('year'));
  my ($q_mon)  = int(scalar $form->param('mon'));

  my $memo_text;
  $query  = "SELECT text ";
  $query .= "FROM memo WHERE year=${q_year} AND month=${q_mon};";
  my $sth = $dbh->prepare($query);
  $sth->execute();
  if ($sth->rows > 0) {
    my @row = $sth->fetchrow_array;
    $memo_text = $row[0] if defined $row[0];
  }
  $sth->finish();

  &header_smp(encode('utf-8', 'メモ編集'));

  my $mes = <<EOF;
<script type="text/javascript">
<!--
  function back_input() {
    document.f_input.mode.value = "view";
    document.f_input.submit();
  }
-->
</script>
<h2>メモ編集</h2>
<form action="$ENV{'SCRIPT_NAME'}" method="POST" name="f_input">
<input type="hidden" name="mode" value="memo_do_edit">
<input type="hidden" name="year" value="${q_year}">
<input type="hidden" name="mon" value="${q_mon}">
<textarea rows="3" tabindex="1" name="memo" style="width: 700px; height: 60px; resize:none">${memo_text}</textarea><br>
<input type="submit" class="submit_button" name="b_submit" tabindex="2" value="変更">&nbsp;
<input type="button" class="normal_button" onClick="back_input()" name="b_back" tabindex="3" value="戻る">
</form>
EOF
  print(encode('utf-8', $mes));

  $dbh->disconnect;

  &tail();
  exit(0);
}

sub do_memoedit() {
  my $dbh = DBI->connect("DBI:mysql:$db_name@$db_host", $db_user, $db_pass, @db_opt);
  my ($q_year) = int(scalar $form->param('year'));
  my ($q_mon)  = int(scalar $form->param('mon'));
  my ($q_memo) = &escape_html(decode('utf-8', scalar($form->param('memo'))));

  if($q_year !~ /^\d+$/ || $q_year < 2000 || $q_year > 2050 ||
     $q_mon  !~ /^\d+$/ || $q_mon  < 0    || $q_mon  > 13   )
  {
    &header(encode('utf-8', "エラー"));
    &error(encode('utf-8', "年／月が不正です。"));
  }

  # 年月レコードの有無を確認
  my $rec_found = 0;
  $query  = "SELECT COUNT(*) FROM memo WHERE year=${q_year} AND month=${q_mon};";
  my $sth = $dbh->prepare($query);
  $sth->execute();
  if ($sth->rows > 0) {
    @row = $sth->fetchrow_array;
    $rec_found = $row[0];
  }
  $sth->finish();

  if($rec_found == 0) {
    if(length($q_memo) == 0) {
      goto END;
    } else {
      $query  = "INSERT INTO memo (year,month,text) VALUES ";
      $query .= "(${q_year},${q_mon},'${q_memo}');";
    }
  } else {
    if(length($q_memo) == 0) {
      $query  = "DELETE FROM  memo ";
      $query .= "WHERE year=${q_year} AND month=${q_mon};";
    } else {
      $query  = "UPDATE memo SET ";
      $query .= "text='${q_memo}' WHERE year=${q_year} AND month=${q_mon};";
    }
  }
  my $sth = $dbh->prepare($query);
  $sth->execute();
  $sth->finish();

END:
  $dbh->disconnect;

  print "Location: $ENV{'REQUEST_SCHEME'}://$ENV{'HTTP_HOST'}$ENV{'SCRIPT_NAME'}?mode=view&year=${q_year}&mon=${q_mon}\n\n";
  exit(0);
}

sub csv() {
  my $filename, $query;
  my $year = scalar($form->param('year'));
  my $mon  = scalar($form->param('mon'));
  if (length($year) == 0 || length($mon) == 0) {
    $filename = "suitou.csv";
   $query  = "SELECT year, month, day, category, summary, expend, income, note ";
   $query .= "FROM webform ORDER BY year, month, day ASC";
  } else {
    $filename = "${year}-${mon}.csv";
   $query  = "SELECT year, month, day, category, summary, expend, income, note ";
   $query .= "FROM webform WHERE year=$year AND month=$mon ORDER BY day ASC";
  }

  print "Content-Type: text/csv\n";
  print "Content-Disposition: attachment; filename=${filename}\n\n";

  my $dbh = DBI->connect("DBI:mysql:$db_name@$db_host", $db_user, $db_pass, @db_opt);

  my $sth = $dbh->prepare($query);
  $sth->execute();

  print '"year","month","day","category","summary","expend","income","note"';
  print "\r\n";
  if ($sth->rows > 0) {
    while(@row = $sth->fetchrow_array) {
      print '"'  . encode('cp932', $row[0]) . '"';
      print ',"' . encode('cp932', $row[1]) . '"';
      print ',"' . encode('cp932', $row[2]) . '"';
      print ',"' . encode('cp932', $row[3]) . '"';
      print ',"' . encode('cp932', $row[4]) . '"';
      print ',"' . encode('cp932', $row[5]) . '"';
      print ',"' . encode('cp932', $row[6]) . '"';
      print ',"' . encode('cp932', $row[7]) . '"';
      print "\r\n";
    }
  }

  $sth->finish();
  $dbh->disconnect;

  exit(0);
}

sub restore_form() {
  print "Content-Type: text/html\n\n";

  my $mes = <<EOF;
<html>
<head>
<title></title>
</head>
<body>
<h3>復元</h3>
<p>バックアップしたcsvファイルを指定して upload をクリックしてください</p>
<form method="POST" action="$ENV{'SCRIPT_NAME'}" enctype="multipart/form-data">
<input type="hidden" name="mode" value="do_restore">
File: <input type="file" name="upload_file">
<input type="submit" value="upload"><br><br>
データ登録:
<input type="radio" name="action" value="add" checked> 追加&nbsp;&nbsp;
<input type="radio" name="action" value="refresh"> 抹消後登録
</form>
</body>
</html>
EOF
  print encode('utf-8', $mes);
  exit(0);
}

sub data_restore() {
  my $line = 0;
  my $guess;
  my $fh = scalar($form->upload('upload_file'));
  my $dbh = DBI->connect("DBI:mysql:$db_name@$db_host", $db_user, $db_pass, @db_opt);
  my $sth;

  if (scalar($form->param('action')) eq "refresh") {
    $sth = $dbh->prepare("DELETE FROM webform;");
    $sth->execute();
  }

  while(my $buffer = <$fh>) {
    $buffer =~ s/\r\n//g;
    # To confirm supported encodes, see /usr/lib64/perl5/Encode/Config.pm
    #$guess = guess_encoding($buffer, qw/7bit-jis shiftjis utf-8/);
    $guess = guess_encoding($buffer, qw/7bit-jis cp932 utf-8/);
    if(ref($guess)) {
      $buffer = decode($guess->name, $buffer);
    } else {
      $buffer = decode('utf-8', $buffer);
    }

    my $idx = 0;
    while(length($buffer) > 0) {
      if (substr($buffer, 0, 1) eq '"') {
        if ((my $pos = index($buffer, '",', 1)) > 0) {
	  $data[$idx] = substr($buffer, 1, $pos-1);
	  $buffer = substr($buffer, $pos+2);
	} elsif (substr($buffer, -1, 1) eq '"') {
	  $data[$idx] = substr($buffer, 1, length($buffer)-2);
	  $buffer = "";
        } else {
          $data[$idx] = $buffer;
	  $buffer = "";
	}
      } else {
        if ((my $pos = index($buffer, ',', 0)) > 0) {
	  $data[$idx] = substr($buffer, 0, $pos);
	  $buffer = substr($buffer, $pos+1);
        } else {
          $data[$idx] = $buffer;
	  $buffer = "";
	}
      }
      $idx++;
    }
    if ($line == 0 ) {
      if ($data[0] ne "year"     ||
	  $data[1] ne "month"    ||
          $data[2] ne "day"      ||
	  $data[3] ne "category" ||
	  $data[4] ne "summary"  ||
	  $data[5] ne "expend"   ||
	  $data[6] ne "income"   ||
	  $data[7] ne "note"
	 )
      {
        &header();
        &error("Invalid csv format");
      }
    } else {
      my $query  = "INSERT INTO webform (year,month,day,category,summary,expend,income,note) ";
         $query .= "VALUES ('$data[0]','$data[1]','$data[2]','$data[3]','$data[4]','$data[5]','$data[6]','$data[7]');";

      $sth = $dbh->prepare($query);
      $sth->execute();
    }

    $line++;
  }
  $sth->finish();
  $dbh->disconnect;

  print "Location: $ENV{'REQUEST_SCHEME'}://$ENV{'HTTP_HOST'}$ENV{'SCRIPT_NAME'}?mode=view\n\n";
  exit(0);
}

sub data_count() {
  my $query  = "SELECT COUNT(*) FROM webform";

  print "Content-Type: text/plain\n\n";

  my $dbh = DBI->connect("DBI:mysql:$db_name@$db_host", $db_user, $db_pass, @db_opt);

  my $sth = $dbh->prepare($query);
  $sth->execute();

  if ($sth->rows > 0) {
    @row = $sth->fetchrow_array;
    print $row[0];
  }

  $sth->finish();
  $dbh->disconnect;

  exit(0);
}

exit(0);
