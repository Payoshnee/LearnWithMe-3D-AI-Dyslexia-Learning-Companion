import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext.jsx'
const links=[['/dashboard','Dashboard'],['/learn','Learn with Wendy'],['/practice','Practice with Bob'],['/games','Phonics Games'],['/reading','Reading'],['/progress','Progress'],['/settings','Settings']]
export default function AppNav(){const {logout}=useAuth();const navigate=useNavigate();return <nav className="app-nav"><Link className="brand-mark" to="/dashboard">LearnWithMe<small>3D AI Dyslexia Learning Companion</small></Link><div>{links.map(([to,label])=><NavLink key={to} to={to}>{label}</NavLink>)}</div><button onClick={async()=>{await logout();navigate('/')}}>Log out</button></nav>}
