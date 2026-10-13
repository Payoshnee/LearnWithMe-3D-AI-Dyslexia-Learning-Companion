const API=import.meta.env.VITE_API_BASE_URL||'http://127.0.0.1:8080'
async function call(path,options={}){const response=await fetch(`${API}${path}`,{credentials:'include',headers:{'Content-Type':'application/json'},...options});const data=await response.json().catch(()=>({}));if(!response.ok)throw new Error(data.detail||'The learning service is unavailable.');return data}
export const answerLesson=body=>call('/api/learning/answer',{method:'POST',body:JSON.stringify(body)})
export const getProgress=()=>call('/api/progress')
export const saveProgress=body=>call('/api/progress',{method:'PUT',body:JSON.stringify(body)})
