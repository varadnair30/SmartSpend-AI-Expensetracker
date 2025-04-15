# Personal Expense Tracker
![Expense Tracker UI](https://github.com/hemantshirsath/Expensetracker/assets/102463335/f31d97f4-4841-44cb-b2af-62286c60a0c9)
![forecast Expense UI ](https://github.com/hemantshirsath/Expensetracker/assets/102463335/c1188567-39c5-4cc1-8916-24f3d3712ee8)

![forecast Expense UI 2](https://github.com/hemantshirsath/Expensetracker/assets/102463335/a2088949-c4f6-4d18-ba23-308ce3ad19f4)
![report ui Expensewise](https://github.com/hemantshirsath/Expensetracker/assets/102463335/c3271340-d3ea-4171-9618-04c8c0a98759)

## Overview

This is a personal expense tracker web application built using Django. It allows users to log their expenses, categorize them, and provides automated expense categorization and future expense prediction features. This README.md file provides instructions for setting up and running the application on your local machine, as well as some additional information about its features and usage.

## Features

- **Expense Logging**: Easily log your daily expenses, including the date, description, amount, and category.

- **Automated Expense Categorization**: The application uses machine learning algorithms to automatically categorize expenses based on their descriptions. This makes it easier to track and manage your spending.

- **Future Expense Prediction**: The application provides predictions for future expenses based on your spending history. This can help you plan your budget more effectively.

- **User Authentication**: Users can create accounts and log in to securely manage their expenses.

## Setup

To run this application locally, follow these steps:

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/personal-expense-tracker.git
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - **Windows**:

     ```bash
     venv\Scripts\activate
     ```

   - **macOS and Linux**:

     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

6. Create a superuser account to access the admin panel:

   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:

   ```bash
   python manage.py runserver
   ```

8. Open your web browser and go to `http://localhost:8000` to access the application.

9. 

Assuming the user already has npm installed, here are the steps for setting up Vite, React, and Tailwind CSS in your project:
Step 1: Install Vite and React

First, in the root directory of your project, initialize a new npm project if you haven't done so already:

npm init -y

Then, install Vite and React:

npm install react react-dom
npm install vite --save-dev

Step 2: Create the Vite Configuration File

In the root directory, create a vite.config.js file for basic Vite configuration:

// vite.config.js
import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8000', // Assuming your Django server is running on port 8000
    },
  },
});

Step 3: Install TailwindCSS

Install Tailwind CSS along with its required dependencies:

npm install tailwindcss postcss autoprefixer --save-dev

Then, generate the Tailwind configuration files:

npx tailwindcss init

This will create a tailwind.config.js file in your project.
Step 4: Configure TailwindCSS

In the tailwind.config.js file, configure your content paths so Tailwind knows where to purge unused styles:

// tailwind.config.js
module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

Step 5: Create Tailwind CSS File

In your src folder (or wherever your main React files are), create a styles/tailwind.css file and add the following lines:

/* styles/tailwind.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

Then, import this file into your main index.js or App.js file:

// src/index.js or src/App.js
import './styles/tailwind.css';

Step 6: Update Your package.json to Add Build & Dev Scripts

Ensure that your package.json includes the necessary scripts to build and run the Vite development server:

{
  "scripts": {
    "dev": "vite", 
    "build": "vite build", 
    "preview": "vite preview"
  }
}

Step 7: Run the Development Server

To start the Vite development server, run the following:

npm run dev

This will launch the development server, and you should be able to access your app at http://localhost:3000 (by default).
Step 8: Build the Production Version

When you’re ready to build the production version of your app, run the following:

npm run build

This will generate the optimized files in the dist folder.

## Usage

1. Create a new account or log in using your superuser account.

2. Start logging your expenses by clicking the "Add Expense" button.

3. Fill in the expense details, including the date, description, amount, and category. You can also leave the category empty, and the application will attempt to automatically categorize it.

4. View your expense history, categorized expenses, and future expense predictions on the dashboard.

5. To access the admin panel, go to `http://localhost:8000/admin/` and log in with your superuser credentials. From the admin panel, you can manage users, categories, and view the database.

## Contributing

If you'd like to contribute to this project, please follow these steps:

1. Fork the repository on GitHub.

2. Create a new branch for your feature or bug fix:

   ```bash
   git checkout -b feature-name
   ```

3. Make your changes and commit them:

   ```bash
   git commit -m "Add new feature"
   ```

4. Push your changes to your forked repository:

   ```bash
   git push origin feature-name
   ```

5. Create a pull request on the original repository to propose your changes.

## Acknowledgments

- Thanks to the Django community for creating such a powerful web framework.

- The automated expense categorization and prediction features are powered by machine learning models, which were trained using various open-source libraries and datasets.

Feel free to customize and enhance this expense tracker according to your needs. Happy budgeting!
