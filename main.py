import os
import sys
import argparse
import zipfile

def create_zip(filename="puzzle.zip"):
    """Create a zip file containing all the necessary files for the jigsaw puzzle app"""
    print(f"Creating {filename}...")
    
    try:
        # Get current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if not current_dir:
            current_dir = os.getcwd()
        print(f"Current directory: {current_dir}")
        
        # Create directories if they don't exist
        os.makedirs(os.path.join(current_dir, 'static', 'pieces'), exist_ok=True)
        os.makedirs(os.path.join(current_dir, 'templates'), exist_ok=True)
        os.makedirs(os.path.join(current_dir, 'uploads'), exist_ok=True)
        
        # Create a README file
        readme_path = os.path.join(current_dir, 'README.md')
        print(f"Creating README at {readme_path}")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("""# ジグソーパズル Web アプリ

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
""")
        
        # Create requirements.txt
        req_path = os.path.join(current_dir, 'requirements.txt')
        print(f"Creating requirements.txt at {req_path}")
        with open(req_path, 'w') as f:
            f.write("""flask==2.0.1
pillow==9.0.0
numpy==1.22.0
jinja2==3.0.1
""")
        
        # Create .gitkeep file for uploads directory
        gitkeep_path = os.path.join(current_dir, 'uploads', '.gitkeep')
        print(f"Creating .gitkeep at {gitkeep_path}")
        with open(gitkeep_path, 'w') as f:
            pass
        
        # Create the zip file
        zip_path = os.path.join(current_dir, filename)
        print(f"Creating zip file at {zip_path}")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Add all Python files
            for file in os.listdir(current_dir):
                if file.endswith('.py') or file == 'README.md' or file == 'requirements.txt':
                    file_path = os.path.join(current_dir, file)
                    print(f"Adding file: {file_path}")
                    zipf.write(file_path, arcname=os.path.basename(file_path))
            
            # Add templates directory
            templates_dir = os.path.join(current_dir, 'templates')
            for root, dirs, files in os.walk(templates_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, current_dir)
                    print(f"Adding template: {arcname}")
                    zipf.write(file_path, arcname=arcname)
            
            # Add static directory
            static_dir = os.path.join(current_dir, 'static')
            for root, dirs, files in os.walk(static_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, current_dir)
                    print(f"Adding static file: {arcname}")
                    zipf.write(file_path, arcname=arcname)
            
            # Add uploads directory (empty structure)
            uploads_dir = os.path.join(current_dir, 'uploads')
            gitkeep_path = os.path.join(uploads_dir, '.gitkeep')
            arcname = os.path.relpath(gitkeep_path, current_dir)
            print(f"Adding uploads structure: {arcname}")
            zipf.write(gitkeep_path, arcname=arcname)
        
        print(f"{filename} created successfully at {zip_path}!")
        return zip_path
    except Exception as e:
        print(f"Error creating zip file: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def output_file(filename):
    """Output the zip file with the given filename - this is the function called from outside"""
    zip_path = create_zip(filename)
    print(f"Zip file created at: {zip_path}")
    return zip_path

def main():
    """Main function to handle the jigsaw puzzle application"""
    parser = argparse.ArgumentParser(description='ジグソーパズル Web アプリ')
    parser.add_argument('--image', type=str, help='画像ファイルのパス')
    parser.add_argument('--rows', type=int, default=4, help='行数 (既定 4)')
    parser.add_argument('--cols', type=int, default=4, help='列数 (既定 4)')
    parser.add_argument('--piece_shape', type=str, default='jigsaw', choices=['square', 'jigsaw'], help='ピース形状 (既定 jigsaw)')
    
    args = parser.parse_args()
    
    # If no arguments are provided, just create the zip file
    if len(sys.argv) == 1:
        output_file("puzzle.zip")
        return
    
    # If image is provided, process it
    if args.image:
        from app import app, split_image
        
        # Create necessary directories
        os.makedirs('static/pieces', exist_ok=True)
        
        # Process the image
        try:
            pieces_info, piece_width, piece_height = split_image(args.image, args.rows, args.cols, args.piece_shape)
            print(f"画像を {args.rows}x{args.cols} のピースに分割しました。")
            print(f"ピースは static/pieces/ ディレクトリに保存されています。")
            
            # Create and output the zip file
            output_file("puzzle.zip")
        except Exception as e:
            print(f"エラー: {str(e)}")
    else:
        print("画像が指定されていません。--image オプションで画像を指定してください。")

if __name__ == "__main__":
    main()
