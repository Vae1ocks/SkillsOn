import styles from "./MainPageLayout.module.scss";
import Header from "./Header";
import Banner from "./Banner";
import Carousel from "./Carousel";
import carouselStyles from "./Carousel.module.scss";
import CourseTypeCard from "./CourseTypeCard";
import CourseCard from "./CourseCard";
import Info from "./Info";
import ReviewCard from "./ReviewCard";
import bgReviewsCarousel from "../../assets/bg_dec_reviews.svg";
import Consultation from "./Consultation";
import { useEffect, useState } from "react";

function MainPage() {
  const [courses, setCourses] = useState([]);

  useEffect(() => {
    const fetchDataForPosts = async () => {
      try {
        const response = await fetch(
          `http://31.128.42.26/courses/?order_by=rating-high-to-low`
        );
        if (!response.ok) {
          throw new Error(`HTTP error: Status ${response.status}`);
        }
        let coursesData = await response.json();
        setCourses(coursesData);
      } catch (err) {
        throw new Error(err.message);
      }
    };

    // fetchDataForPosts();
  }, []);

  return (
    <div className={styles.mainPage}>
      <Header />
      <Banner />
      <Carousel
        title="Выбирай направление, которое подходит именно тебе"
        amountPerPage={4}
        style={carouselStyles.courseType}
      >
        <CourseTypeCard imgSrc={0} />
        <CourseTypeCard imgSrc={1} />
        <CourseTypeCard imgSrc={2} />
        <CourseTypeCard imgSrc={3} />
        <CourseTypeCard imgSrc={2} />
        <CourseTypeCard imgSrc={2} />
        <CourseTypeCard imgSrc={3} />
        <CourseTypeCard imgSrc={2} />
        <CourseTypeCard imgSrc={0} />
        <CourseTypeCard imgSrc={1} />
        <CourseTypeCard imgSrc={2} />
        <CourseTypeCard imgSrc={3} />
        <CourseTypeCard imgSrc={2} />
        <CourseTypeCard imgSrc={2} />
        <CourseTypeCard imgSrc={3} />
        <CourseTypeCard imgSrc={2} />
        <CourseTypeCard imgSrc={2} />
        <CourseTypeCard imgSrc={2} />
        <CourseTypeCard imgSrc={3} />
        <CourseTypeCard imgSrc={2} />
      </Carousel>
      <Carousel
        title="Популярные курсы"
        amountPerPage={3}
        style={`${carouselStyles.courseType} ${carouselStyles.popularCourses}`}
      >
        {/* {courses &&
          courses.map((course) => (
            <CourseCard
              key={course.id}
              wide={true}
              level={course.level}
              title={course.category.title}
              author={course.author_name}
              rating={0}
              reviews={0}
              price={
                course.price.slice(
                  course.price.length - 3,
                  course.price.length
                ) == ".00"
                  ? Number(course.price)
                  : course.price
              }
            />
          ))} */}
        <CourseCard
          wide={true}
          level="Junior"
          title="Frontend-разработчик"
          author="Иван И."
          rating={4.8}
          reviews={23}
          price={2500}
        />
        <CourseCard
          wide={true}
          level="Junior"
          title="UX/UI дизайнер"
          author="Иван И."
          rating={4.7}
          reviews={25}
          price={2500}
        />
        <CourseCard
          wide={true}
          level="Middle"
          title="Аналитик данных"
          author="Иван И."
          rating={4.8}
          reviews={32}
          price={2500}
        />
      </Carousel>
      <Info />
      <Carousel
        title="Отзывы о курсах"
        amountPerPage={3}
        style={`${carouselStyles.courseType} ${carouselStyles.reviews}`}
        bg={bgReviewsCarousel}
      >
        <ReviewCard
          name="Иванов Иван"
          course="Frontend-разработчик"
          rating={4}
          review="Недавно завершил курс «Фронтенд-разработка для начинающих» и остался очень доволен. Преподаватель отлично объясняет материал, делая сложные концепции доступными. Курс включает множество практических заданий, которые помогают сразу применять полученные знания. Поддержка на форуме и в чатах была на высоте, всегда можно было получить ответ на любой вопрос. Рекомендую этот курс всем, кто хочет быстро и эффективно освоить основы фронтенд-разработки!"
        />
        <ReviewCard
          name="Иванов Иван"
          course="Frontend-разработчик"
          rating={4}
          review="Недавно завершил курс «Фронтенд-разработка для начинающих» и остался очень доволен."
        />
        <ReviewCard
          name="Иванов Иван"
          course="Frontend-разработчик"
          rating={4}
          review="Недавно завершил курс «Фронтенд-разработка для начинающих» и остался очень доволен. Преподаватель отлично объясняет материал, делая сложные концепции доступными. Курс включает множество практических заданий, которые помогают сразу применять полученные знания. Поддержка на форуме и в чатах была на высоте, всегда можно было получить ответ на любой вопрос. Рекомендую этот курс всем, кто хочет быстро и эффективно освоить основы фронтенд-разработки!"
        />
        <ReviewCard
          name="Иванов Иван"
          course="Frontend-разработчик"
          rating={4}
          review="Недавно завершил курс «Фронтенд-разработка для начинающих» и остался очень доволен. Преподаватель отлично объясняет материал, делая сложные концепции доступными. Курс включает множество практических заданий, которые помогают сразу применять полученные знания. Поддержка на форуме и в чатах была на высоте, всегда можно было получить ответ на любой вопрос. Рекомендую этот курс всем, кто хочет быстро и эффективно освоить основы фронтенд-разработки!"
        />
        <ReviewCard
          name="Иванов Иван"
          course="Frontend-разработчик"
          rating={4}
          review="Недавно завершил курс «Фронтенд-разработка для начинающих» и остался очень доволен."
        />
        <ReviewCard
          name="Иванов Иван"
          course="Frontend-разработчик"
          rating={4}
          review="Недавно завершил курс «Фронтенд-разработка для начинающих» и остался очень доволен. Преподаватель отлично объясняет материал, делая сложные концепции доступными. Курс включает множество практических заданий, которые помогают сразу применять полученные знания. Поддержка на форуме и в чатах была на высоте, всегда можно было получить ответ на любой вопрос. Рекомендую этот курс всем, кто хочет быстро и эффективно освоить основы фронтенд-разработки!"
        />
        <ReviewCard
          name="Иванов Иван"
          course="Frontend-разработчик"
          rating={4}
          review="Недавно завершил курс «Фронтенд-разработка для начинающих» и остался очень доволен. Преподаватель отлично объясняет материал, делая сложные концепции доступными. Курс включает множество практических заданий, которые помогают сразу применять полученные знания. Поддержка на форуме и в чатах была на высоте, всегда можно было получить ответ на любой вопрос. Рекомендую этот курс всем, кто хочет быстро и эффективно освоить основы фронтенд-разработки!"
        />
        <ReviewCard
          name="Иванов Иван"
          course="Frontend-разработчик"
          rating={4}
          review="Недавно завершил курс «Фронтенд-разработка для начинающих» и остался очень доволен."
        />
        <ReviewCard
          name="Иванов Иван"
          course="Frontend-разработчик"
          rating={4}
          review="Недавно завершил курс «Фронтенд-разработка для начинающих» и остался очень доволен. Преподаватель отлично объясняет материал, делая сложные концепции доступными. Курс включает множество практических заданий, которые помогают сразу применять полученные знания. Поддержка на форуме и в чатах была на высоте, всегда можно было получить ответ на любой вопрос. Рекомендую этот курс всем, кто хочет быстро и эффективно освоить основы фронтенд-разработки!"
        />
        <ReviewCard
          name="Иванов Иван"
          course="Frontend-разработчик"
          rating={4}
          review="Недавно завершил курс «Фронтенд-разработка для начинающих» и остался очень доволен. Преподаватель отлично объясняет материал, делая сложные концепции доступными. Курс включает множество практических заданий, которые помогают сразу применять полученные знания. Поддержка на форуме и в чатах была на высоте, всегда можно было получить ответ на любой вопрос. Рекомендую этот курс всем, кто хочет быстро и эффективно освоить основы фронтенд-разработки!"
        />
        <ReviewCard
          name="Иванов Иван"
          course="Frontend-разработчик"
          rating={4}
          review="Недавно завершил курс «Фронтенд-разработка для начинающих» и остался очень доволен."
        />
        <ReviewCard
          name="Иванов Иван"
          course="Frontend-разработчик"
          rating={4}
          review="Недавно завершил курс «Фронтенд-разработка для начинающих» и остался очень доволен. Преподаватель отлично объясняет материал, делая сложные концепции доступными. Курс включает множество практических заданий, которые помогают сразу применять полученные знания. Поддержка на форуме и в чатах была на высоте, всегда можно было получить ответ на любой вопрос. Рекомендую этот курс всем, кто хочет быстро и эффективно освоить основы фронтенд-разработки!"
        />
        <ReviewCard
          name="Иванов Иван"
          course="Frontend-разработчик"
          rating={4}
          review="Недавно завершил курс «Фронтенд-разработка для начинающих» и остался очень доволен. Преподаватель отлично объясняет материал, делая сложные концепции доступными. Курс включает множество практических заданий, которые помогают сразу применять полученные знания. Поддержка на форуме и в чатах была на высоте, всегда можно было получить ответ на любой вопрос. Рекомендую этот курс всем, кто хочет быстро и эффективно освоить основы фронтенд-разработки!"
        />
        <ReviewCard
          name="Иванов Иван"
          course="Frontend-разработчик"
          rating={4}
          review="Недавно завершил курс «Фронтенд-разработка для начинающих» и остался очень доволен."
        />
        <ReviewCard
          name="Иванов Иван"
          course="Frontend-разработчик"
          rating={4}
          review="Недавно завершил курс «Фронтенд-разработка для начинающих» и остался очень доволен. Преподаватель отлично объясняет материал, делая сложные концепции доступными. Курс включает множество практических заданий, которые помогают сразу применять полученные знания. Поддержка на форуме и в чатах была на высоте, всегда можно было получить ответ на любой вопрос. Рекомендую этот курс всем, кто хочет быстро и эффективно освоить основы фронтенд-разработки!"
        />
      </Carousel>
      <Consultation />
    </div>
  );
}

export default MainPage;
