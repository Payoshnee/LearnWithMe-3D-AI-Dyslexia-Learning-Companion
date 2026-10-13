import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext.jsx'
import HomePage from '../pages/HomePage.jsx'
import LoginPage from '../pages/LoginPage.jsx'
import RegisterPage from '../pages/RegisterPage.jsx'
import DoodleSelectPage from '../pages/DoodleSelectPage.jsx'
import CompanionStagePage from '../pages/CompanionStagePage.jsx'
import { DashboardPage, GamesPage, LearnPage, PracticePage, ProgressPage, ReadingPage, SettingsPage } from '../pages/LearningPages.jsx'

function Protected({children}){const {user,loading}=useAuth();if(loading)return <main className="video-page"><div className="page-content"><p className="loader">Opening LearnWithMe…</p></div></main>;return user?children:<Navigate to="/login" replace/>}
export default function App(){return <Routes><Route path="/" element={<HomePage/>}/><Route path="/login" element={<LoginPage/>}/><Route path="/register" element={<RegisterPage/>}/><Route path="/choose" element={<Protected><DoodleSelectPage/></Protected>}/><Route path="/stage" element={<Protected><CompanionStagePage/></Protected>}/><Route path="/dashboard" element={<Protected><DashboardPage/></Protected>}/><Route path="/learn" element={<Protected><LearnPage/></Protected>}/><Route path="/practice" element={<Protected><PracticePage/></Protected>}/><Route path="/games" element={<Protected><GamesPage/></Protected>}/><Route path="/reading" element={<Protected><ReadingPage/></Protected>}/><Route path="/progress" element={<Protected><ProgressPage/></Protected>}/><Route path="/settings" element={<Protected><SettingsPage/></Protected>}/><Route path="*" element={<Navigate to="/" replace/>}/></Routes>}
