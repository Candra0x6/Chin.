import Dashboard from '@/components/WireframeDashboard'
import React from 'react'

function layout({children}: {children: React.ReactNode}) {
  return (
    <>
    <Dashboard >{children}</Dashboard>
    </>
  )
}

export default layout