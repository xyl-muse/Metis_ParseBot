import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Contents from './pages/Contents'
import ContentDetail from './pages/ContentDetail'
import LearningRecords from './pages/LearningRecords'
import Settings from './pages/Settings'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="contents" element={<Contents />} />
        <Route path="contents/:id" element={<ContentDetail />} />
        <Route path="learning" element={<LearningRecords />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}

export default App
