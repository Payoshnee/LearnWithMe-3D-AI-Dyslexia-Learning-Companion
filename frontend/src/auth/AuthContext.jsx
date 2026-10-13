import { createContext, useContext, useEffect, useState } from 'react'
import * as auth from '../services/authApi'
const Context=createContext(null)
export function AuthProvider({children}){const [user,setUser]=useState(null),[loading,setLoading]=useState(true);useEffect(()=>{auth.session().then(setUser).catch(()=>setUser(null)).finally(()=>setLoading(false))},[]);const value={user,loading,login:async data=>setUser(await auth.login(data)),register:async data=>setUser(await auth.register(data)),logout:async()=>{await auth.logout();setUser(null)}};return <Context.Provider value={value}>{children}</Context.Provider>}
export const useAuth=()=>useContext(Context)
