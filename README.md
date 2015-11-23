# 出納帳プログラム

# 始めに

このプログラムはWebブラウザから毎日の支出・収入を入力して、毎月の出納を
確認するためのものです。所謂、家計簿プログラムです

表示されるメッセージなど、実装の関係から対応言語は日本語のみです

This program supports Japanese only.

# 必要な環境

* CGIスクリプトが実行可能なWebサーバー
* Perl実行環境
* MySQL

# 使い方

インストールしたWebサーバーのsuitou.cgiのURLを開いてください

# インストール

## データベースの作成

mysqlを管理者権限で開き、以下のSQLを実行します

実行例
<pre>
# mysql -u root -p
mysql> CREATE DATABASE suitou;
mysql> CREATE TABLE suitou.webform (
    -> id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    -> year INT NOT NULL,
    -> month INT NOT NULL,
    -> day INT NOT NULL,
    -> category VARCHAR(16) NOT NULL,
    -> summary VARCHAR(512) NOT NULL,
    -> expend MEDIUMINT UNSIGNED DEFAULT 0 NOT NULL,
    -> income MEDIUMINT UNSIGNED DEFAULT 0 NOT NULL,
    -> note VARCHAR(512) );
mysql> GRANT SELECT,UPDATE,INSERT,DELETE ON suitou.* TO mysql@localhost IDENTIFIED BY 'mysql';
mysql> CREATE INDEX idx_year_mon ON webform (year, month);
mysql> CREATE INDEX idx_year ON webform (year);
mysql> CREATE INDEX idx_month ON webform (month);
</pre>

## CGIスクリプトのインストール

本ディレクトリの cgi-bin のファイルをWebサーバーのCGI実行可能なディレクトリ
にコピーしてください

# 注意

本プログラムには認証機能がありません。
外部からアクセス可能な環境で実行する際には十分な対策を行った上でご使用ください

# ライセンス

このスクリプトは Apache License 2.0 です
