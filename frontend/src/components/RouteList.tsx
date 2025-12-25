import React from 'react'

export default function RouteList({ addresses, setAddresses } : any){
  const update = (i:number, key:string, value:string) => {
    const arr = [...addresses]
    arr[i] = { ...arr[i], [key]: value }
    setAddresses(arr)
  }
  const add = ()=> setAddresses([ ...addresses, {street:'', city:'', postal_code:''} ])
  const remove = (i:number)=> setAddresses(addresses.filter((_:any, idx:number)=>idx!==i))

  return (
    <div className="route-list">
      {addresses.map((a:any,i:number)=> (
        <div className="addr-row" key={i}>
          <input placeholder="Street" value={a.street} onChange={e=>update(i,'street',e.target.value)} />
          <input placeholder="City" value={a.city} onChange={e=>update(i,'city',e.target.value)} />
          <input placeholder="Postal" value={a.postal_code||''} onChange={e=>update(i,'postal_code',e.target.value)} />
          <button className="btn small" onClick={()=>remove(i)}>Remove</button>
        </div>
      ))}
      <div style={{marginTop:10}}><button className="btn" onClick={add}>Add Address</button></div>
    </div>
  )
}
