// import { chromium } from 'playwright';
// import SelectorFinder from 'playwright-selector-finder';

// (async () => {
//   const browser = await chromium.launch();
//   const page = await browser.newPage();
//   const finder = new SelectorFinder();

//   await finder.init();

//   await page.goto('https://preprod-arunodayakurtis.zupain.com/product-list');

//   // Example: Find selector for "product name"
//   const productNameSelector = await finder.findSelector('product name');
//   console.log('Product Name Selector:', productNameSelector.selector);

//   // Example: Find selector for "product price"
//   const productPriceSelector = await finder.findSelector('product price');
//   console.log('Product Price Selector:', productPriceSelector.selector);

//   await finder.close();
//   await browser.close();
// })();
