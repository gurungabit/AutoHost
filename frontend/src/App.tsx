import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Builder } from './pages/Builder';
import { Scripts } from './pages/Scripts';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/scripts" replace />} />
        <Route path="/scripts" element={<Scripts />} />
        <Route path="/builder" element={<Builder />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
