import os
import random
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from PIL import Image, ImageDraw
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PIECES_FOLDER'] = os.path.join('static', 'pieces')

# Create necessary directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PIECES_FOLDER'], exist_ok=True)

def create_jigsaw_mask(width, height, edge_size=20):
    """Create a jigsaw-like mask for a puzzle piece"""
    mask = Image.new('L', (width, height), 255)
    draw = ImageDraw.Draw(mask)
    
    # Define the tab/blank pattern for each edge
    edges = {
        'top': random.choice([1, -1]),     # 1: tab, -1: blank
        'right': random.choice([1, -1]),
        'bottom': random.choice([1, -1]),
        'left': random.choice([1, -1])
    }
    
    # Draw the edges
    for edge, direction in edges.items():
        if edge == 'top' and direction == 1:
            # Draw a tab on top edge
            draw.ellipse((width//2 - edge_size, -edge_size, 
                         width//2 + edge_size, edge_size), fill=0)
        elif edge == 'top' and direction == -1:
            # Draw a blank on top edge
            draw.ellipse((width//2 - edge_size, -edge_size, 
                         width//2 + edge_size, edge_size), fill=255)
            
        if edge == 'right' and direction == 1:
            # Draw a tab on right edge
            draw.ellipse((width - edge_size, height//2 - edge_size, 
                         width + edge_size, height//2 + edge_size), fill=0)
        elif edge == 'right' and direction == -1:
            # Draw a blank on right edge
            draw.ellipse((width - edge_size, height//2 - edge_size, 
                         width + edge_size, height//2 + edge_size), fill=255)
            
        if edge == 'bottom' and direction == 1:
            # Draw a tab on bottom edge
            draw.ellipse((width//2 - edge_size, height - edge_size, 
                         width//2 + edge_size, height + edge_size), fill=0)
        elif edge == 'bottom' and direction == -1:
            # Draw a blank on bottom edge
            draw.ellipse((width//2 - edge_size, height - edge_size, 
                         width//2 + edge_size, height + edge_size), fill=255)
            
        if edge == 'left' and direction == 1:
            # Draw a tab on left edge
            draw.ellipse((-edge_size, height//2 - edge_size, 
                         edge_size, height//2 + edge_size), fill=0)
        elif edge == 'left' and direction == -1:
            # Draw a blank on left edge
            draw.ellipse((-edge_size, height//2 - edge_size, 
                         edge_size, height//2 + edge_size), fill=255)
    
    return mask, edges

def split_image(image_path, rows, cols, piece_shape):
    """Split an image into puzzle pieces"""
    # Load and convert image to RGBA
    img = Image.open(image_path).convert('RGBA')
    
    # Calculate piece dimensions
    piece_width = img.width // cols
    piece_height = img.height // rows
    
    pieces_info = []
    
    # Create a dictionary to store edge information
    edge_map = {}
    
    # First pass: create edge patterns for all pieces
    for row in range(rows):
        for col in range(cols):
            piece_id = f"{row}_{col}"
            edge_map[piece_id] = {
                'top': None,
                'right': None,
                'bottom': None,
                'left': None
            }
    
    # Second pass: assign edge patterns ensuring they match adjacent pieces
    for row in range(rows):
        for col in range(cols):
            piece_id = f"{row}_{col}"
            
            # Top edge
            if row > 0:
                # Match with the bottom edge of the piece above
                edge_map[piece_id]['top'] = -edge_map[f"{row-1}_{col}"]['bottom']
            else:
                # Top row pieces have flat top edges
                edge_map[piece_id]['top'] = 0
                
            # Left edge
            if col > 0:
                # Match with the right edge of the piece to the left
                edge_map[piece_id]['left'] = -edge_map[f"{row}_{col-1}"]['right']
            else:
                # Leftmost pieces have flat left edges
                edge_map[piece_id]['left'] = 0
                
            # For bottom and right edges of pieces not on the border, randomly assign
            if row < rows - 1:
                edge_map[piece_id]['bottom'] = random.choice([1, -1])
            else:
                # Bottom row pieces have flat bottom edges
                edge_map[piece_id]['bottom'] = 0
                
            if col < cols - 1:
                edge_map[piece_id]['right'] = random.choice([1, -1])
            else:
                # Rightmost pieces have flat right edges
                edge_map[piece_id]['right'] = 0
    
    # Third pass: create and save the pieces
    for row in range(rows):
        for col in range(cols):
            # Calculate piece position
            left = col * piece_width
            upper = row * piece_height
            right = left + piece_width
            lower = upper + piece_height
            
            # Crop the piece from the original image
            piece = img.crop((left, upper, right, lower))
            
            piece_id = f"{row}_{col}"
            piece_filename = f"piece_{row}_{col}.png"
            piece_path = os.path.join(app.config['PIECES_FOLDER'], piece_filename)
            
            if piece_shape == 'jigsaw':
                # Create a base mask for the piece (fully opaque)
                mask = Image.new('L', (piece_width, piece_height), 255)
                draw = ImageDraw.Draw(mask)
                
                # Apply edge patterns
                edge_size = min(piece_width, piece_height) // 5
                
                # Top edge
                if edge_map[piece_id]['top'] == 1:
                    # Tab on top
                    draw.ellipse((piece_width//2 - edge_size, -edge_size, 
                                 piece_width//2 + edge_size, edge_size), fill=0)
                elif edge_map[piece_id]['top'] == -1:
                    # Blank on top
                    draw.ellipse((piece_width//2 - edge_size, -edge_size, 
                                 piece_width//2 + edge_size, edge_size), fill=255)
                
                # Right edge
                if edge_map[piece_id]['right'] == 1:
                    # Tab on right
                    draw.ellipse((piece_width - edge_size, piece_height//2 - edge_size, 
                                 piece_width + edge_size, piece_height//2 + edge_size), fill=0)
                elif edge_map[piece_id]['right'] == -1:
                    # Blank on right
                    draw.ellipse((piece_width - edge_size, piece_height//2 - edge_size, 
                                 piece_width + edge_size, piece_height//2 + edge_size), fill=255)
                
                # Bottom edge
                if edge_map[piece_id]['bottom'] == 1:
                    # Tab on bottom
                    draw.ellipse((piece_width//2 - edge_size, piece_height - edge_size, 
                                 piece_width//2 + edge_size, piece_height + edge_size), fill=0)
                elif edge_map[piece_id]['bottom'] == -1:
                    # Blank on bottom
                    draw.ellipse((piece_width//2 - edge_size, piece_height - edge_size, 
                                 piece_width//2 + edge_size, piece_height + edge_size), fill=255)
                
                # Left edge
                if edge_map[piece_id]['left'] == 1:
                    # Tab on left
                    draw.ellipse((-edge_size, piece_height//2 - edge_size, 
                                 edge_size, piece_height//2 + edge_size), fill=0)
                elif edge_map[piece_id]['left'] == -1:
                    # Blank on left
                    draw.ellipse((-edge_size, piece_height//2 - edge_size, 
                                 edge_size, piece_height//2 + edge_size), fill=255)
                
                # Apply the mask to the piece
                piece.putalpha(mask)
            
            # Save the piece
            piece.save(piece_path)
            
            # Store piece information
            pieces_info.append({
                'id': piece_id,
                'row': row,
                'col': col,
                'filename': piece_filename,
                'width': piece_width,
                'height': piece_height,
                'correctX': left,
                'correctY': upper
            })
    
    # Shuffle the pieces for initial random placement
    random.shuffle(pieces_info)
    
    return pieces_info, piece_width, piece_height

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get parameters
    rows = int(request.form.get('rows', 4))
    cols = int(request.form.get('cols', 4))
    piece_shape = request.form.get('piece_shape', 'jigsaw')
    
    # Save the uploaded file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Process the image
    try:
        pieces_info, piece_width, piece_height = split_image(file_path, rows, cols, piece_shape)
        
        # Get the original image dimensions
        img = Image.open(file_path)
        img_width, img_height = img.size
        
        return jsonify({
            'success': True,
            'pieces': pieces_info,
            'imageWidth': img_width,
            'imageHeight': img_height,
            'pieceWidth': piece_width,
            'pieceHeight': piece_height,
            'rows': rows,
            'cols': cols
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/pieces/<filename>')
def serve_piece(filename):
    return send_from_directory(app.config['PIECES_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
