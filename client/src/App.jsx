import LoginPage from './Pages/auth/Login/index'
import RegisterPage from './Pages/auth/Register/index'
import { Route, Routes } from 'react-router';
import PrivateRoute from './utilits/router/PrivateRoute';
import MainPage from './Pages/MainPage';
import s from './App.module.scss'
import CoursesPage from './Pages/Courses';
function App() {


 return (
   <div className={s.app}>
     <Routes>
       <Route element={<PrivateRoute />}>
         <Route path="main" element={<MainPage/>} />
       </Route>
       <Route path="login" element={<LoginPage />} />
       <Route path="register" element={<RegisterPage />} />
       <Route path="courses" element={<CoursesPage />} />


     </Routes>
   </div>
 )
}


export default App