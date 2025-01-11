document.addEventListener('DOMContentLoaded', () => {
    const carousel = document.querySelector('.carousel-container');
    const cards = document.querySelectorAll('.game-card');
    const prevButton = document.querySelector('.prev');
    const nextButton = document.querySelector('.next');
    
    // Clone enough cards for smooth infinite scroll
    const totalClones = 2; // Number of sets to clone on each side
    
    // Clone cards and add to both ends
    for (let i = 0; i < totalClones; i++) {
        cards.forEach(card => {
            const startClone = card.cloneNode(true);
            const endClone = card.cloneNode(true);
            carousel.appendChild(startClone);
            carousel.insertBefore(endClone, carousel.firstChild);
        });
    }

    let currentIndex = cards.length * totalClones; // Start from middle set
    let cardWidth = carousel.offsetWidth / 3;
    let isTransitioning = false;

    function updateCarousel(smooth = true) {
        carousel.style.transition = smooth ? 'transform 0.5s ease' : 'none';
        carousel.style.transform = `translateX(-${currentIndex * (cardWidth + 32)}px)`; // 32px is the gap
    }

    function handleTransitionEnd() {
        isTransitioning = false;
        carousel.style.transition = 'none';
        
        // Reset to middle set if we've gone too far in either direction
        if (currentIndex <= totalClones) {
            currentIndex = cards.length * totalClones;
            updateCarousel(false);
        } else if (currentIndex >= cards.length * (totalClones * 2)) {
            currentIndex = cards.length * totalClones;
            updateCarousel(false);
        }
        
        // Re-enable transitions after position reset
        setTimeout(() => {
            carousel.style.transition = 'transform 0.5s ease';
        }, 10);
    }

    function moveNext() {
        if (isTransitioning) return;
        isTransitioning = true;
        currentIndex++;
        updateCarousel();
    }

    function movePrev() {
        if (isTransitioning) return;
        isTransitioning = true;
        currentIndex--;
        updateCarousel();
    }

    // Initial position
    updateCarousel(false);

    // Event Listeners
    carousel.addEventListener('transitionend', handleTransitionEnd);
    prevButton?.addEventListener('click', movePrev);
    nextButton?.addEventListener('click', moveNext);

    // Auto-play feature with pause on hover
    let autoPlayInterval;

    function startAutoPlay() {
        autoPlayInterval = setInterval(moveNext, 2000); // Change 3000 to a lower numberfor faster scrolling
    }

    function stopAutoPlay() {
        clearInterval(autoPlayInterval);
    }

    carousel.addEventListener('mouseenter', stopAutoPlay);
    carousel.addEventListener('mouseleave', startAutoPlay);

    // Start autoplay initially
    startAutoPlay();

    // Handle window resize
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            cardWidth = carousel.offsetWidth / 3;
            updateCarousel(false);
        }, 100);
    });

    // Touch events for mobile swipe
    let touchStartX = 0;
    let touchEndX = 0;

    carousel.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
        stopAutoPlay();
    }, { passive: true });

    carousel.addEventListener('touchmove', (e) => {
        touchEndX = e.touches[0].clientX;
    }, { passive: true });

    carousel.addEventListener('touchend', () => {
        const swipeDistance = touchEndX - touchStartX;
        if (Math.abs(swipeDistance) > 50) { // Minimum swipe distance
            if (swipeDistance > 0) {
                movePrev();
            } else {
                moveNext();
            }
        }
        startAutoPlay();
    });

    // Add after existing code
    const testimonialSwiper = new Swiper('.testimonials-slider .swiper-container', {
        slidesPerView: 1,
        spaceBetween: 30,
        loop: true,
        autoplay: {
            delay: 3000,
            disableOnInteraction: false,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        }
    });
});