import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import '@/app/globals.css';
import { RadarApp } from '@/components/radar-app';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RadarApp />
  </StrictMode>,
);
