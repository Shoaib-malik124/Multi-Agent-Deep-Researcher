import React from 'react'
import { useAuth } from '@clerk/clerk-react'
import Dashbackground from './Dashbackground.jsx'
import Alert  from '@mui/material/Alert';
import { useState,useEffect } from 'react';
import { DocumentCard } from './DocumentCard.jsx';
import { PaginationTray } from './paginationTray.jsx';
import axios from 'axios'


function Documents() {
  const { getToken }=useAuth()
  
  const [documents,setDocuments]=useState([])
  const [page_num,setPage_num]=useState(1)
  const [total_pages,setTotal_pages]=useState(1)
  const [loading,setLoading]=useState(false)
  const [error,setError]=useState(null)

  const Backend_url=import.meta.env.VITE_BACKEND_URL // 

  const getDocuments=async (page_num=1)=>{
    setLoading(true)
    setError(null)
    try{
      const token=await getToken()
      const Route_url=`${Backend_url}/api/documents`
      const response=await axios.get(Route_url,
        {
          params:{
            page_num:page_num
          },
          headers:{
            'Authorization':`Bearer ${token}`
          }
        }
      )
      
      if(response.data){
        console.log(response.data); 
        setDocuments(response.data.documents)
        setTotal_pages(response.data.total_pages)
      }
    }
    catch(error){
      console.log(error)
      if (error.response) {
        setError(`Error ${error.response.status}: ${error.response.data.detail}`)
      } else {
        setError('Connection error — please try again')
      }
    }
    finally{
      setLoading(false)
    }
  }

  useEffect(()=>{
    getDocuments(page_num)
  },[page_num])

  if (error) return (
    <div className="flex items-center justify-center h-screen text-red-500">
        {error}
    </div>
  )

  return (
    <main className="relative flex min-h-[calc(100vh-64px)] items-center justify-center overflow-hidden bg-slate-50 px-4 py-10 sm:px-6 sm:py-16">

      <Dashbackground />
        <div className="min-h-screen bg-gray-50 p-4 md:p-8">
            <h1 className="text-2xl font-bold text-gray-800 mb-6">My Research</h1>

            {/* Document grid */}
            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[...Array(6)].map((_, i) => (
                        <div key={i} className="bg-gray-200 rounded-xl h-40 animate-pulse"/>
                    ))}
                </div>
            ) : documents.length===0 ? (
                <div className="text-center text-gray-400 mt-20">
                    No research reports yet
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {documents.map(doc => (
                        <DocumentCard key={doc._id} doc={doc} />
                    ))}
                </div>
            )}

            {/* Pagination tray — only show if more than one page */}
            {total_pages > 1 && (
                <PaginationTray
                    currentPage={page_num}
                    totalPages={total_pages}
                    onPageChange={setPage_num}
                />
            )}
        </div>
    </main>
  )
}

export default Documents