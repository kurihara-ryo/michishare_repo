# Michishare
旅行プラン共有アプリ（Django）

## 概要
Michishare は、観光地での「どこに何があるかは分かるけれど、**どう回れば効率よく・楽しく観光できるのかが分からない**」という課題を解決するために開発したアプリです。

InstagramやSNSでは、特定のスポット単体の情報は非常に詳しく紹介されています。しかし、**周辺スポットとの繋がり・巡る順序・実際に何を見て何を食べたか**など、観光全体の流れが分かる情報は少ないのが現状です。

そこで Michishare では、ユーザーが実際に巡った **観光ルート・順路・訪問スポット・食べたものや体験したこと** を自由に投稿・共有できる仕組みを作りました。

これにより、
- 初めて訪れる場所でも回る順番がわかる  
- 他の人の“成功したルート”や“楽しめたルート”を参考にできる  
- 地域全体の回遊性が向上し、観光地活性化につながる  
- インバウンド観光客の利便性向上にも貢献  

といった価値を提供することを目指しています。

---

## 主な機能（予定含む）
- 観光ルートの投稿
- スポットの登録・タグ付け
- ルートの閲覧・保存
- 写真・コメントのシェア
- 観光地ごとの人気ルートランキング
- 地図上でのルート可視化（今後実装予定）

---

## 使用技術
- **Framework**: Django
- **Frontend**: HTML / CSS / JavaScript
- **Database**: SQLite（開発環境）
- **Auth**: Django Authentication

---

## 環境構築

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver