import csv

def generate_svg_alternative(csv_path, output_path):
    # Load and parse CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]

    # Use Enrollment vs Out-of-school
    # SE.PRM.ENRR: Primary enrollment, gross (%)
    # ROFST.1.CP: Out-of-school rate, primary (%)
    enrollment = sorted([(int(r['year']), float(r['value'])) for r in rows if r['indicator_code'] == 'SE.PRM.ENRR'])
    oos_rate = sorted([(int(r['year']), float(r['value'])) for r in rows if r['indicator_code'] == 'ROFST.1.CP'])

    if not enrollment or not oos_rate:
        print("Error: Missing data for visualization.")
        return

    # Plot dimensions
    width, height = 900, 500
    padding = 80
    chart_w, chart_h = width - 2*padding, height - 2*padding

    # Scales
    all_years = [d[0] for d in enrollment + oos_rate]
    min_y, max_y = min(all_years), max(all_years)
    
    # Both are percentages
    min_val, max_val = 0, 100

    def x_scale(y): return padding + (y - min_y) / (max_y - min_y) * chart_w
    def y_scale(v): return height - padding - (v / 100) * chart_h

    # Start SVG
    svg = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background:#fff; font-family:Arial, sans-serif;">']
    
    # Background and Grid
    svg.append(f'<rect width="{width}" height="{height}" fill="white" />')
    for y in range(0, 101, 20): 
        yp = y_scale(y)
        svg.append(f'<line x1="{padding}" y1="{yp}" x2="{width-padding}" y2="{yp}" stroke="#eee" />')
        svg.append(f'<text x="{padding-10}" y="{yp+5}" text-anchor="end" font-size="10" fill="#666">{y}%</text>')

    # Breakpoints
    breakpoints = [(2011, 'Syrian War'), (2019, 'Collapse'), (2020, 'Blast')]
    for by, label in breakpoints:
        xp = x_scale(by)
        svg.append(f'<line x1="{xp}" y1="{padding}" x2="{xp}" y2="{height-padding}" stroke="#ccc" stroke-dasharray="4" />')
        svg.append(f'<text x="{xp+5}" y="{padding+20}" fill="#999" font-size="12" font-weight="bold" transform="rotate(90, {xp+5}, {padding+20})">{label}</text>')

    # Enrollment Line (Blue)
    pts = " ".join([f"{x_scale(d[0])},{y_scale(d[1])}" for d in enrollment])
    svg.append(f'<polyline points="{pts}" fill="none" stroke="#2563eb" stroke-width="3" />')
    for d in enrollment:
        svg.append(f'<circle cx="{x_scale(d[0])}" cy="{y_scale(d[1])}" r="3" fill="#2563eb" />')

    # Out-of-school Line (Orange)
    pts = " ".join([f"{x_scale(d[0])},{y_scale(d[1])}" for d in oos_rate])
    svg.append(f'<polyline points="{pts}" fill="none" stroke="#f97316" stroke-width="3" />')
    for d in oos_rate:
        svg.append(f'<rect x="{x_scale(d[0])-3}" y="{y_scale(d[1])-3}" width="6" height="6" fill="#f97316" />')

    # Axes
    svg.append(f'<line x1="{padding}" y1="{height-padding}" x2="{width-padding}" y2="{height-padding}" stroke="#333" stroke-width="2" />') # X
    svg.append(f'<line x1="{padding}" y1="{padding}" x2="{padding}" y2="{height-padding}" stroke="#333" stroke-width="2" />') # Y

    # Labels
    svg.append(f'<text x="{width/2}" y="{padding/2}" text-anchor="middle" font-size="20" font-weight="bold">Enrollment vs. Out-of-School Rates (Primary)</text>')

    # X-Axis Years
    for year in range(min_y, max_y + 1, 2):
        svg.append(f'<text x="{x_scale(year)}" y="{height-padding+20}" text-anchor="middle" font-size="11">{year}</text>')

    # Legend
    svg.append(f'<rect x="{padding+20}" y="{padding+20}" width="15" height="15" fill="#2563eb" />')
    svg.append(f'<text x="{padding+40}" y="{padding+32}" font-size="12">Gross Enrollment Rate (%)</text>')
    
    svg.append(f'<rect x="{padding+20}" y="{padding+45}" width="15" height="15" fill="#f97316" />')
    svg.append(f'<text x="{padding+40}" y="{padding+57}" font-size="12">Out-of-School Rate (%)</text>')

    svg.append('</svg>')
    
    with open(output_path, 'w') as f:
        f.write("\n".join(svg))
    print(f"✅ Comparison SVG generated at {output_path}")

if __name__ == "__main__":
    generate_svg_alternative('lebanon_education_data.csv', 'enrollment_vs_oos.svg')
