import s from './AuthLayout.module.scss'


const AuthLayout = ({children}) => {
   return (
       <div className={s.layout}>
           <div className={s.wrapper}>
               {children}
           </div>
       </div>
   )
}


export default AuthLayout