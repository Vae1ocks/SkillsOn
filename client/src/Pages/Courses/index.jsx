import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import style from './Courses.module.scss'
import CoursesLayout from "./CoursesLayout";

function CoursesPage() {
const [posts, setPosts] = useState([]);

        useEffect(() => {
            fetch('https://jsonplaceholder.typicode.com/posts')
            .then (res => {
            return res.json()
            })
            .then(data => {
            setPosts(data)
            
            });

        }, []);

  return (
    <>
    <CoursesLayout>
        <div className={style.container}>
       {posts.map(post => (
          <div key={post.id}>
          <p>{post.title}</p>
          <p>{post.body}</p>
          <Link to={`/post/${post.id}`}>
          Комментарии
          </Link>
          </div>
  ))}
            </div>

  </CoursesLayout>
  </>
  );
}

export default CoursesPage