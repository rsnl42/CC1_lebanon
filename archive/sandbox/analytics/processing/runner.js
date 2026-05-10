import { fetchAll } from './lebanon-education-fetcher.js';
import fs from 'fs';

async function main() {
  try {
    const dataset = await fetchAll();
    
    // Save dataset
    fs.writeFileSync('lebanon_education_data.json', JSON.stringify(dataset, null, 2));
    console.log('\n💾 Dataset saved to lebanon_education_data.json');

    // Save errors separately for the user
    if (dataset.errors && dataset.errors.length > 0) {
      fs.writeFileSync('fetch_errors.json', JSON.stringify(dataset.errors, null, 2));
      console.log(`⚠️ ${dataset.errors.length} errors saved to fetch_errors.json`);
    } else {
      console.log('✅ No errors encountered.');
    }
  } catch (err) {
    console.error('Fatal error during fetch:', err);
    process.exit(1);
  }
}

main();
