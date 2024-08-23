import s from './Courses.module.scss'


// eslint-disable-next-line react/prop-types
const CoursesLayout = ({children}) => {
   return (
       <div className={s.layout}>
           <div className={s.wrapper}>
               {children}
           </div>
       </div>
   )
}


export default CoursesLayout