import { useState } from 'react'
import './App.css'
import Header from './components/header/Header'
import OrderStatus from './components/orderStatus/OrderStatus'
import NearbyOrders from './components/nearbyOrders/NearbyOrders';
import RequestOrder from './components/requestOrder/RequestOrder';
import 'bootstrap/dist/css/bootstrap.min.css';



function App() {

  return (
    <div>
      <Header />
      <OrderStatus />
      <NearbyOrders />
      <RequestOrder/>
      
    </div>
  )
}

export default App
