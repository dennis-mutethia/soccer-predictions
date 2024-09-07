
import uuid
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def create_image_table(rows, total_amount):
    # Define the size of the image
    width = 600
    row_height = 40
    header_height = 50
    footer_height = 50
    padding = 10
    height = header_height + row_height * len(rows) + footer_height  # Add extra space for header, rows, and footer

    # Create a new blank image with white background
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    # Load a TrueType font (you can use any TTF font you have)
    try:
        header_font = ImageFont.truetype("arial.ttf", 20)  # Bold for header
        cell_font = ImageFont.truetype("arial.ttf", 18)    # Regular font for cells
    except IOError:
        # Fallback to default font if .ttf is not available
        header_font = ImageFont.load_default()
        cell_font = ImageFont.load_default()

    # Define column positions (adjust for a more compact layout)
    col_positions = [0, 160, 320, 450, 600]  # End of last column is the image width

    # Draw header with blue background and borders
    draw.rectangle([(0, 0), (width, header_height)], fill="dodgerblue")
    headers = ["RECEIVED AT", "SENDER NAME", "MPESA CODE", "AMOUNT"]
    for i, col_text in enumerate(headers):
        x_position = (col_positions[i] + col_positions[i + 1]) // 2  # Center alignment
        bbox = draw.textbbox((0, 0), col_text, font=header_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        y_position = (header_height - text_height) // 2
        draw.text((x_position - text_width // 2, y_position), col_text, fill="white", font=header_font)
        # Draw vertical lines
        draw.line([(col_positions[i], 0), (col_positions[i], header_height)], fill="black", width=2)

    # Draw horizontal line after header
    draw.line([(0, header_height), (width, header_height)], fill="black", width=2)

    # Draw rows with borders
    for row_index, row in enumerate(rows):
        y_position = header_height + row_index * row_height
        # Draw background for alternate rows (optional, can be removed for a cleaner look)
        if row_index % 2 == 0:
            draw.rectangle([(0, y_position), (width, y_position + row_height)], fill="white")

        for i, col_text in enumerate(row):
            bbox = draw.textbbox((0, 0), col_text, font=cell_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            if i == 3:  # Right-align the "AMOUNT" column
                x_position = col_positions[i + 1] - text_width - padding
            else:  # Center-align other columns
                x_position = (col_positions[i] + col_positions[i + 1]) // 2 - text_width // 2

            cell_y_position = y_position + (row_height - text_height) // 2
            draw.text((x_position, cell_y_position), col_text, fill="black", font=cell_font)

            # Draw vertical lines
            draw.line([(col_positions[i], y_position), (col_positions[i], y_position + row_height)], fill="black", width=2)

        # Draw horizontal line for each row
        #draw.line([(0, y_position + row_height), (width, y_position + row_height)], fill="black", width=2)

    # Draw footer with blue background and borders
    footer_y_position = header_height + row_height * len(rows)
    draw.rectangle([(0, footer_y_position), (width, footer_y_position + footer_height)], fill="darkgreen")

    # Draw "TOTAL" text inside the first three columns
    total_label = "TOTAL"
    bbox_total = draw.textbbox((0, 0), total_label, font=header_font)
    text_width_total = bbox_total[2] - bbox_total[0]
    x_position_total = (col_positions[0] + col_positions[3]) // 2 - text_width_total // 2  # Center in colspan of 3
    draw.text((x_position_total, footer_y_position + (footer_height - (bbox_total[3] - bbox_total[1])) // 2), total_label, fill="white", font=header_font)

    # Draw total amount in the last column, right-aligned
    bbox_amount = draw.textbbox((0, 0), total_amount, font=header_font)
    amount_width = bbox_amount[2] - bbox_amount[0]
    y_position_amount = footer_y_position + (footer_height - (bbox_amount[3] - bbox_amount[1])) // 2
    draw.text((col_positions[4] - amount_width - padding, y_position_amount), total_amount, fill="white", font=header_font)

    # Draw vertical lines for the footer
    draw.line([(col_positions[0], footer_y_position), (col_positions[0], footer_y_position + footer_height)], fill="black", width=2)
    draw.line([(col_positions[3], footer_y_position), (col_positions[3], footer_y_position + footer_height)], fill="black", width=2)
    draw.line([(col_positions[4], footer_y_position), (col_positions[4], footer_y_position + footer_height)], fill="black", width=2)

    # Draw horizontal line for the footer
    draw.line([(0, footer_y_position + footer_height), (width, footer_y_position + footer_height)], fill="black", width=2)

    # Save image to file
    image_name = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(datetime.now()))).split('-')[0]
    img.save(f'{image_name}.png')

# Sample data rows
rows = [
    ["2024-09-07 17:54", "JOHN DOE", "MXPTFG567F", "10,000"],
    ["2024-09-07 17:54", "JANE DOE", "YXPTFG567Z", "2,000"],
    ["2024-09-07 17:54", "JANE DOE", "YXPTFG567Z", "800"],
    ["2024-09-07 17:54", "JANE DOE", "YXPTFG567Z", "50"],
    ["2024-09-07 17:54", "JANE DOE", "YXPTFG567Z", "102,000"],
    ["2024-09-07 17:54", "JANE DOE", "YXPTFG567Z", "800"],
    ["2024-09-07 17:54", "JANE DOE", "YXPTFG567Z", "50"],
    ["2024-09-07 17:54", "JOHN DOE", "MXPTFG567F", "10,000"],
    ["2024-09-07 17:54", "JANE DOE", "YXPTFG567Z", "2,000"],
    ["2024-09-07 17:54", "JANE DOE", "YXPTFG567Z", "800"],
    ["2024-09-07 17:54", "JANE DOE", "YXPTFG567Z", "50"],
    ["2024-09-07 17:54", "JANE DOE", "YXPTFG567Z", "102,000"],
    ["2024-09-07 17:54", "JANE DOE", "YXPTFG567Z", "800"],
    ["2024-09-07 17:54", "JANE DOE", "YXPTFG567Z", "50"]
]

# Total amount to be displayed in the footer
total_amount = "3,128,000"

# Generate the styled image table with center-aligned headers and total
create_image_table(rows, total_amount)
