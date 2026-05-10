import csv

def generate_svg(csv_path, output_path):
    # Load and parse CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]

    # Extract indicators
    migration_raw = sorted([(int(r['year']), float(r['value'])) for r in rows if r['indicator_code'] == 'SM.POP.NETM'])
    enrollment_pri = sorted([(int(r['year']), float(r['value'])) for r in rows if r['indicator_code'] == 'SE.PRM.ENRR'])
    enrollment_sec = sorted([(int(r['year']), float(r['value'])) for r in rows if r['indicator_code'] == 'SE.SEC.ENRR'])

    # Calculate Cumulative Migration Stock (starting from 0 in 2000)
    migration_stock = []
    current_stock = 0
    for year, val in migration_raw:
        current_stock += val
        migration_stock.append((year, max(0, current_stock)))

    # Plot dimensions
    width, height = 900, 500
    padding = 80
    chart_w, chart_h = width - 2*padding, height - 2*padding

    # Scales
    all_years = [d[0] for d in migration_stock + enrollment_pri + enrollment_sec]
    min_y, max_y = min(all_years), max(all_years)
    
    max_ref = max(d[1] for d in migration_stock)
    min_enr = 30 # Lowered to accommodate secondary enrollment which is usually lower
    max_enr = 100

    def x_scale(y): return padding + (y - min_y) / (max_y - min_y) * chart_w
    def y_ref_scale(v): return height - padding - (v / max_ref) * chart_h
    def y_enr_scale(v): return height - padding - ((v - min_enr) / (max_enr - min_enr)) * chart_h

    # Start SVG
    svg = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background:#fff; font-family:Arial, sans-serif;">']
    
    # Background and Grid
    svg.append(f'<rect width="{width}" height="{height}" fill="white" />')
    for y in range(min_enr, max_enr + 1, 10): 
        yp = y_enr_scale(y)
        svg.append(f'<line x1="{padding}" y1="{yp}" x2="{width-padding}" y2="{yp}" stroke="#eee" />')

    # Breakpoints
    breakpoints = [(2011, 'Syrian War'), (2019, 'Collapse'), (2020, 'Blast')]
    for by, label in breakpoints:
        xp = x_scale(by)
        svg.append(f'<line x1="{xp}" y1="{padding}" x2="{xp}" y2="{height-padding}" stroke="#ccc" stroke-dasharray="4" />')
        svg.append(f'<text x="{xp+5}" y="{padding+20}" fill="#999" font-size="12" font-weight="bold" transform="rotate(90, {xp+5}, {padding+20})">{label}</text>')

    # 1. Migration Stock Line (Red)
    pts = " ".join([f"{x_scale(d[0])},{y_ref_scale(d[1])}" for d in migration_stock])
    svg.append(f'<polyline points="{pts}" fill="none" stroke="#dc2626" stroke-width="3" />')
    for d in migration_stock:
        svg.append(f'<circle cx="{x_scale(d[0])}" cy="{y_ref_scale(d[1])}" r="3" fill="#dc2626" />')

    # 2. Primary Enrollment Line (Blue)
    pts = " ".join([f"{x_scale(d[0])},{y_enr_scale(d[1])}" for d in enrollment_pri])
    svg.append(f'<polyline points="{pts}" fill="none" stroke="#2563eb" stroke-width="3" />')
    for d in enrollment_pri:
        svg.append(f'<rect x="{x_scale(d[0])-3}" y="{y_enr_scale(d[1])-3}" width="6" height="6" fill="#2563eb" />')

    # 3. Secondary Enrollment Line (Green)
    pts = " ".join([f"{x_scale(d[0])},{y_enr_scale(d[1])}" for d in enrollment_sec])
    svg.append(f'<polyline points="{pts}" fill="none" stroke="#16a34a" stroke-width="3" stroke-dasharray="5,2" />')
    for d in enrollment_sec:
        # Triangle marker
        xp, yp = x_scale(d[0]), y_enr_scale(d[1])
        svg.append(f'<polygon points="{xp},{yp-5} {xp-4},{yp+3} {xp+4},{yp+3}" fill="#16a34a" />')

    # Axes
    svg.append(f'<line x1="{padding}" y1="{height-padding}" x2="{width-padding}" y2="{height-padding}" stroke="#333" stroke-width="2" />') # X
    svg.append(f'<line x1="{padding}" y1="{padding}" x2="{padding}" y2="{height-padding}" stroke="#dc2626" stroke-width="2" />') # Y1
    svg.append(f'<line x1="{width-padding}" y1="{padding}" x2="{width-padding}" y2="{height-padding}" stroke="#2563eb" stroke-width="2" />') # Y2

    # Labels
    svg.append(f'<text x="{width/2}" y="{padding/2}" text-anchor="middle" font-size="20" font-weight="bold">Lebanon: Migration vs. School Enrollment</text>')
    svg.append(f'<text x="{padding-10}" y="{height/2}" text-anchor="middle" transform="rotate(-90, {padding-10}, {height/2})" fill="#dc2626" font-size="12" font-weight="bold">Cumulative Net Migration (Stock)</text>')
    svg.append(f'<text x="{width-padding+50}" y="{height/2}" text-anchor="middle" transform="rotate(90, {width-padding+50}, {height/2})" fill="#2563eb" font-size="12" font-weight="bold">Enrollment Rate (%)</text>')

    # X-Axis Years
    for year in range(min_y, max_y + 1, 2):
        svg.append(f'<text x="{x_scale(year)}" y="{height-padding+20}" text-anchor="middle" font-size="11">{year}</text>')

    # Legend
    svg.append(f'<rect x="{padding+20}" y="{height-padding-100}" width="15" height="15" fill="#dc2626" />')
    svg.append(f'<text x="{padding+40}" y="{height-padding-88}" font-size="12">Migration Stock</text>')
    
    svg.append(f'<rect x="{padding+20}" y="{height-padding-75}" width="15" height="15" fill="#2563eb" />')
    svg.append(f'<text x="{padding+40}" y="{height-padding-63}" font-size="12">Primary Enrollment (%)</text>')
    
    svg.append(f'<path d="M {padding+20} {height-padding-35} L {padding+27.5} {height-padding-45} L {padding+35} {height-padding-35} Z" fill="#16a34a" />')
    svg.append(f'<text x="{padding+40}" y="{height-padding-38}" font-size="12">Secondary Enrollment (%)</text>')

    svg.append('</svg>')
    
    with open(output_path, 'w') as f:
        f.write("\n".join(svg))
    print(f"✅ Updated SVG chart generated at {output_path}")

if __name__ == "__main__":
    generate_svg('lebanon_education_data.csv', 'crisis_correlation.svg')
