const path = require('path');

module.exports = {
  entry: './path/to/your/script.js', // Entry point of your JavaScript file
  output: {
    filename: 'bundle.js', // Output bundled JavaScript file
    path: path.resolve(__dirname, 'dist'), // Output directory
  },
};
