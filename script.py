import random, os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

# This code is generated with Gemini 3 Flash Preview to built a fast script to print # cards for the traditional italian Christmas game 'Tombola' to enjoy the winter 
# holidays; some variations of the code are made to make it more readble.
# The given prompt is the following, also an image of an existing card is uploaded:
#
# Write a python script to create the cards of the tipic italian Christmas game:
# Tombola. As you can see each page is made up of 6 cards; each one is composed of a
# grid 9 x 3, with randomized numbers between 1 and 90 (inclusive them). The goal is
# to fill up each card with 15 randomized numbers. Try to implement a good
# randomization based on a seed for example about the current local time and date.
# It would be great if the cards are printed in a pdf file, considering that each
# page has 12 cards (two set of 6 cards for each page), so that I can print a couple
# for each A4 paper; you can omit the text in the image upper each card ('Lettera'
# and 'Cartella'). Include a solution to specify the total number of pages of cards
# that are printed out (remember that in one page it's printing 2 set of cards).
# Try the keep the same style of the uploaded image, maybe modernise a little bit.

# --- STYLE & MEASUREMENT CONFIGURATION ---
STYLES = {
    'label_font': ("Helvetica-Oblique", 8),
    'header_font': ("Helvetica-Bold", 14),
    'number_font': ("Helvetica-Bold", 24),
    'logo_size': (50 * mm, 11 * mm),
    'offsets': {
        'labels_y': 10 * mm,        # Height of the labels above the cards
        'header_y_offset': 5 * mm,  # Vertical shift for the Main Text Header
        'logo_y_offset': 8 * mm     # Vertical shift for the Logo
    }
}

def generate_tombola_serie():
    """
    Generates a 'Serie' of 6 cards ensuring every number from 1 to 90 
    appears exactly once, with 5 numbers per row and 15 per card.
    """
    # Create pools for each column [1-9], [10-19]...[80-90]
    pools = [list(range(1, 10))] + [list(range(i*10, i*10+10)) for i in range(1, 8)] + [list(range(80, 91))]
    for p in pools:
        random.shuffle(p)

    # Logic to distribute 90 slots across 18 rows (6 cards * 3 rows)
    # Col counts: Col 0 has 9 slots, Col 1-7 have 10, Col 8 has 11.
    col_counts = [9, 10, 10, 10, 10, 10, 10, 10, 11]
    
    success = False
    while not success:
        row_slots = [set() for _ in range(18)]
        row_fill_counts = [0] * 18
        fail = False
        
        # Distribute column availability into rows
        for col_idx, count in enumerate(col_counts):
            # Find rows that don't have this column yet and have < 5 numbers
            available_rows = [i for i in range(18) if row_fill_counts[i] < 5]
            if len(available_rows) < count:
                fail = True
                break
            
            chosen_rows = random.sample(available_rows, count)
            for r in chosen_rows:
                row_slots[r].add(col_idx)
                row_fill_counts[r] += 1
        
        if not fail and all(c == 5 for c in row_fill_counts):
            success = True

    # Populate slots with numbers and group into 6 cards
    cards = []
    for c_idx in range(6):
        card_matrix = [[None]*9 for _ in range(3)]
        for r_offset in range(3):
            r_idx = c_idx * 3 + r_offset
            for col_idx in sorted(list(row_slots[r_idx])):
                card_matrix[r_offset][col_idx] = pools[col_idx].pop()
        
        # Sort numbers vertically within columns of the SAME card (standard rule)
        for col in range(9):
            vals = sorted([card_matrix[row][col] for row in range(3) if card_matrix[row][col] is not None])
            idx = 0
            for row in range(3):
                if card_matrix[row][col] is not None:
                    card_matrix[row][col] = vals[idx]
                    idx += 1
        cards.append(card_matrix)
    
    return cards

def draw_header_block(c, x_l, x_r, y_base, header_text, logo_path, sub_l, sub_r):
    """
    Helper function to draw the sub-texts and the main header/logo 
    centered between two horizontal boundaries.
    """
    x_mid = (x_l + x_r) / 2
    y_label = y_base + STYLES['offsets']['labels_y']

    # Draw small italic labels (justified left and right)
    c.setFont(*STYLES['label_font'])
    c.drawString(x_l, y_label, sub_l)
    c.drawRightString(x_r, y_label, sub_r)

    # 2. Draw center element (logo or text)
    if logo_path and os.path.exists(logo_path):
        logo_w, logo_h = STYLES['logo_size']
        # Centering math: middle - half of width
        l_x = x_mid - (logo_w / 2)
        l_y = y_label - STYLES['offsets']['logo_y_offset']
        c.drawImage(logo_path, l_x, l_y, width=logo_w, height=logo_h, 
                    preserveAspectRatio=True, anchor='c', mask='auto')
    elif header_text:
        c.setFont(*STYLES['header_font'])
        text_y = y_label - STYLES['offsets']['header_y_offset']
        c.drawCentredString(x_mid, text_y, header_text)

def create_pdf(num_pages, filename, upper_left, upper_right, header_text=None, logo_path=None):
    
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Dimensions
    card_w = 90 * mm
    card_h = 42 * mm
    margin_x = 10 * mm
    margin_top = 15 * mm
    gap_x = 10 * mm
    gap_y = 5 * mm
    
    for _ in range(num_pages):
        # Boundaries for the two columns (sets) of cards
        set1_left, set1_right = margin_x, margin_x + card_w
        set2_left, set2_right = margin_x + card_w + gap_x, width - margin_x
        
        # Draw headers for each set at the top of the page
        y_header_pos = height - margin_top

        # Draw labels for both sets
        columns = [(set1_left, set1_right), (set2_left, set2_right)]
        for x_l, x_r in columns:
            draw_header_block(c, x_l, x_r, y_header_pos, header_text, logo_path, upper_left, upper_right)

        # Generate two series (6+6 = 12 cards) for the page
        page_cards = generate_tombola_serie() + generate_tombola_serie()
        
        for i, card in enumerate(page_cards):
            # Position calculation (2 columns, 6 rows)
            col_pos = i // 6
            row_pos = i % 6
            
            x = margin_x + col_pos * (card_w + gap_x)
            y = height - margin_top - (row_pos + 1) * card_h - row_pos * gap_y
            
            # Draw thick outer border
            c.setLineWidth(1.5)
            c.rect(x, y, card_w, card_h)
            
            # Draw grid lines
            c.setLineWidth(0.5)
            cell_w = card_w / 9
            cell_h = card_h / 3
            for j in range(1, 9): # Vertical
                c.line(x + j*cell_w, y, x + j*cell_w, y + card_h)
            for j in range(1, 3): # Horizontal
                c.line(x, y + j*cell_h, x + card_w, y + j*cell_h)
            
            # Fill cards with numbers
            c.setFont(*STYLES['number_font'])
            for r_idx in range(3):
                for c_idx in range(9):
                    val = card[r_idx][c_idx]
                    if val:
                        # Draw number centered in cell
                        # (2 - r_idx) flips the row index because PDF Y starts at bottom
                        tx = x + c_idx * cell_w + cell_w/2
                        ty = y + (2 - r_idx) * cell_h + cell_h/2 - 8 
                        c.drawCentredString(tx, ty, str(val))
                        
        c.showPage()
    
    c.save()
    print(f"Successfully generated {num_pages} pages ({num_pages * 12} cards) in {filename}")

if __name__ == "__main__":
    # SPECIFY TOTAL PAGES HERE
    PAGES = 1
    MY_TITLE = "My title"
    UPPER_LEFT = "My upper left title"
    UPPER_RIGHT = "My upper right title"
    OUTPUT_NAME = "Cards"
    if not OUTPUT_NAME.lower().endswith('.pdf'):
        OUTPUT_NAME += ".pdf"
    LOGO_PATH = ""

    create_pdf(PAGES, OUTPUT_NAME, UPPER_LEFT, UPPER_RIGHT, MY_TITLE, LOGO_PATH)