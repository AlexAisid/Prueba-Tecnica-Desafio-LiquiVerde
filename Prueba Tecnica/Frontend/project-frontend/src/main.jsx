import React from 'react';
import ReactDOM from 'react-dom/client';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import App from './App';
import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import '@mantine/charts/styles.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <MantineProvider
      theme={{
        primaryColor: 'green',
        colors: {
          green: [
            '#e8f5e9',
            '#c8e6c9',
            '#a5d6a7',
            '#81c784',
            '#66bb6a',
            '#4caf50',
            '#43a047',
            '#388e3c',
            '#2e7d32',
            '#1b5e20',
          ],
        },
      }}
    >
      <Notifications position="top-right" />
      <App />
    </MantineProvider>
  </React.StrictMode>
);