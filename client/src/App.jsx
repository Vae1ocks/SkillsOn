import LoginPage from './components/auth/Login/index'
import RegisterPage from './components/auth/Register/index'
import { Route, Routes } from 'react-router';
import PrivateRoute from './utilits/router/PrivateRoute';
import MainPage from './components/MainPage';
import s from './App.module.scss'
import CoursesPage from './components/Courses';
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