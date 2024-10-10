import { useState } from "react";
import styles from "./Carousel.module.scss";
import leftArrowIcon from "../../assets/left_arrow_icon.svg";
import rightArrowIcon from "../../assets/right_arrow_icon.svg";

function SwitchPageButton({ active, switchPage }) {
  return (
    <button onClick={switchPage}>
      <svg
        width="12"
        height="12"
        viewBox="0 0 12 12"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle cx="6" cy="6" r="6" fill={active ? "#2871ee" : "#CCCCCC"} />
      </svg>
    </button>
  );
}

function Carousel({ children, title, amountPerPage, style, bg = null }) {
  const [currentPage, setCurrentPage] = useState(0);

  const renderedChildren = children.slice(
    0 + currentPage * amountPerPage,
    amountPerPage + currentPage * amountPerPage
  );

  return (
    <div className={style}>
      <img className={styles.bg} src={bg} />
      <p className={styles.title}>{title}</p>
      {Math.ceil(children.length / amountPerPage) > 1 && (
        <button
          className={styles.back}
          onClick={() =>
            currentPage == 0
              ? setCurrentPage(Math.ceil(children.length / amountPerPage) - 1)
              : setCurrentPage(currentPage - 1)
          }
        >
          <img src={leftArrowIcon} alt="back" />
        </button>
      )}
      {Math.ceil(children.length / amountPerPage) > 1 && (
        <button
          className={styles.forward}
          onClick={() =>
            currentPage == Math.ceil(children.length / amountPerPage) - 1
              ? setCurrentPage(0)
              : setCurrentPage(currentPage + 1)
          }
        >
          <img src={rightArrowIcon} alt="forward" />
        </button>
      )}
      <div className={styles.content}>{renderedChildren}</div>
      {children.length / amountPerPage > 1 && (
        <div className={styles.pageButtons}>
          {Array.from(
            Array(Math.ceil(children.length / amountPerPage)).keys()
          ).map((page) => (
            <SwitchPageButton
              key={page}
              active={currentPage == page}
              switchPage={() => setCurrentPage(page)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default Carousel;
