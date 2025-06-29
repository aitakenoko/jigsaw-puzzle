# PowerShell script to create puzzle.zip

# Create directories if they don't exist
New-Item -ItemType Directory -Force -Path "static\pieces" | Out-Null
New-Item -ItemType Directory -Force -Path "templates" | Out-Null
New-Item -ItemType Directory -Force -Path "uploads" | Out-Null

# Create .gitkeep file for uploads directory
New-Item -ItemType File -Force -Path "uploads\.gitkeep" | Out-Null

# Create requirements.txt
Set-Content -Path "requirements.txt" -Value "flask==2.0.1`npillow==9.0.0`nnumpy==1.22.0`njinja2==3.0.1" -Encoding UTF8

# Create README.md
$readmeContent = @'
# ジグソーパズル Web アプリ

## 概要
このアプリケーションは、画像をNxMのピースに分割したジグソーパズルを作成します。

## 使い方
1. `python app.py` を実行してサーバーを起動します
2. ブラウザで `http://localhost:5000` にアクセスします
3. 画像をアップロードし、行数・列数・ピース形状を選択します
4. 「パズルを作成」ボタンをクリックしてパズルを開始します
5. ピースをドラッグ＆ドロップして正しい位置に配置します
6. 全てのピースが正しい位置に配置されると、完成のお祝いメッセージが表示されます

## 必要なパッケージ
- Flask
- Pillow
- NumPy

## インストール方法
```
pip install flask pillow numpy
```
'@
Set-Content -Path "README.md" -Value $readmeContent -Encoding UTF8

# Create the zip file
$compress = @{
  Path = "app.py", "main.py", "README.md", "requirements.txt", "templates", "static", "uploads"
  CompressionLevel = "Optimal"
  DestinationPath = "puzzle.zip"
}
Compress-Archive @compress -Force

Write-Host "puzzle.zip created successfully!"
