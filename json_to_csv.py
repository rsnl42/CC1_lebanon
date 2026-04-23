import json
import csv
import os

def convert_json_to_csv(json_path, csv_path):
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    # Prepare CSV headers
    # We include metadata for each indicator as columns for easy filtering in Excel/Pandas
    headers = ['year', 'indicator_code', 'indicator_label', 'unit', 'source', 'angle', 'value']

    records = []
    indicators = data.get('indicators', {})

    for code, info in indicators.items():
        label = info.get('label', '')
        unit = info.get('unit', '')
        source = info.get('source', '')
        angle = info.get('angle', '')
        series = info.get('series', [])

        for point in series:
            records.append({
                'year': point.get('year'),
                'indicator_code': code,
                'indicator_label': label,
                'unit': unit,
                'source': source,
                'angle': angle,
                'value': point.get('value')
            })

    # Sort records by year then indicator code
    records.sort(key=lambda x: (x['year'], x['indicator_code']))

    # Write to CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(records)

    print(f"✅ Successfully converted {json_path} to {csv_path}")
    print(f"📊 Total rows written: {len(records)}")

if __name__ == "__main__":
    convert_json_to_csv('lebanon_education_data.json', 'lebanon_education_data.csv')
