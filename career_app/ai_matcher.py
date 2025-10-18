import re
from difflib import SequenceMatcher
from collections import Counter
import math
from .models import Applicant, Vacancy, IdealCandidateProfile, IdealVacancyProfile, AISearchMatch


class AIMatcher:

    @staticmethod
    def extract_key_concepts(text):
        """Извлекает ключевые концепции из текста (смысловые блоки)"""
        if not text:
            return []

        # Приводим к нижнему регистру
        text = text.lower()

        # Разбиваем на предложения и фразы
        sentences = re.split(r'[.!?;]\s*', text)

        concepts = []
        for sentence in sentences:
            if len(sentence.strip()) < 10:  # Пропускаем слишком короткие
                continue

            # Разбиваем на значимые фразы (по запятым, союзам)
            phrases = re.split(r'[,:;]\s+|\s+и\s+|\s+или\s+', sentence)

            for phrase in phrases:
                phrase = phrase.strip()
                if len(phrase) > 3:  # Минимальная длина фразы
                    concepts.append(phrase)

        return concepts

    @staticmethod
    def calculate_semantic_similarity(text1, text2):
        """Вычисляет смысловую схожесть между текстами"""
        if not text1 or not text2:
            return 0

        # Извлекаем ключевые концепции
        concepts1 = AIMatcher.extract_key_concepts(text1)
        concepts2 = AIMatcher.extract_key_concepts(text2)

        if not concepts1 or not concepts2:
            return 0

        # Считаем совпадение концепций
        total_similarity = 0
        matched_pairs = []

        for concept1 in concepts1:
            best_match_score = 0
            best_match_concept = ""

            for concept2 in concepts2:
                # Сравниваем концепции по сходству последовательностей
                similarity = SequenceMatcher(None, concept1, concept2).ratio()
                if similarity > best_match_score:
                    best_match_score = similarity
                    best_match_concept = concept2

            if best_match_score > 0.6:  # Порог значимого совпадения
                total_similarity += best_match_score
                matched_pairs.append((concept1, best_match_concept, best_match_score))

        # Нормализуем результат
        max_possible = max(len(concepts1), len(concepts2))
        if max_possible == 0:
            return 0

        final_similarity = (total_similarity / max_possible) * 100
        return int(final_similarity)

    @staticmethod
    def extract_requirements(text):
        """Извлекает требования/навыки из текста автоматически"""
        if not text:
            return []

        text_lower = text.lower()
        requirements = []

        # Паттерны для извлечения требований
        patterns = [
            r'требования?[:\s]*([^.!?]+)[.!?]',
            r'навыки?[:\s]*([^.!?]+)[.!?]',
            r'умение[:\s]*([^.!?]+)[.!?]',
            r'обязанности?[:\s]*([^.!?]+)[.!?]',
            r'знание[:\s]*([^.!?]+)[.!?]',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                # Разбиваем на отдельные требования
                items = re.split(r'[,;]|\s+и\s+', match)
                requirements.extend([item.strip() for item in items if len(item.strip()) > 2])

        # Если не нашли по паттернам, берем все существительные и глаголы
        if not requirements:
            words = re.findall(r'\b[а-яa-z]{3,}\b', text_lower)
            # Фильтруем слишком общие слова
            general_words = {'работа', 'опыт', 'знание', 'умение', 'требование', 'навык'}
            requirements = [word for word in words if word not in general_words]

        return list(set(requirements))  # Убираем дубликаты

    @staticmethod
    def match_candidate_with_profile(applicant, ideal_profile):
        """Сопоставляет кандидата с идеальным профилем"""
        # Используем полный текст резюме из новых полей
        applicant_text = applicant.get_full_resume_text()

        # Смысловая схожесть
        semantic_similarity = AIMatcher.calculate_semantic_similarity(
            applicant_text,
            ideal_profile.ideal_resume
        )

        # Извлекаем и сравниваем требования
        applicant_skills = AIMatcher.extract_requirements(applicant_text)
        required_skills = AIMatcher.extract_requirements(
            ideal_profile.ideal_resume + " " + ideal_profile.required_skills
        )

        # Схожесть требований
        skills_match = AIMatcher.calculate_skills_match(applicant_skills, required_skills)

        # Опыт работы (определяем по контексту)
        experience_match = AIMatcher.match_experience_by_context(
            applicant_text,
            ideal_profile.experience_level
        )

        # Взвешенная оценка с акцентом на смысл
        final_score = int(
            semantic_similarity * 0.6 +  # Главное - смысловая схожесть
            skills_match * 0.3 +  # Конкретные требования
            experience_match * 0.1  # Уровень опыта
        )

        return {
            'semantic_similarity': semantic_similarity,
            'skills_match': skills_match,
            'experience_match': experience_match,
            'final_score': final_score,
            'matched_concepts': applicant_skills[:10],  # Топ-10 совпадений
            'explanation': AIMatcher.generate_explanation(
                semantic_similarity, skills_match, experience_match
            )
        }

    @staticmethod
    def calculate_skills_match(skills1, skills2):
        """Сравнивает наборы навыков"""
        if not skills2:
            return 100

        # Считаем схожесть каждого навыка с каждым
        total_match = 0

        for skill2 in skills2:
            best_match = 0
            for skill1 in skills1:
                similarity = SequenceMatcher(None, skill1, skill2).ratio()
                if similarity > best_match:
                    best_match = similarity

            total_match += best_match

        return int((total_match / len(skills2)) * 100)

    @staticmethod
    def match_experience_by_context(text, target_experience):
        """Определяет уровень опыта по контексту"""
        text_lower = text.lower()

        # Ключевые слова для разных уровней
        experience_keywords = {
            'junior': ['стажер', 'начинающий', 'младший', 'без опыта', 'учусь'],
            'middle': ['опыт', 'работал', 'разрабатывал', 'создавал', 'участвовал'],
            'senior': ['ведущий', 'старший', 'руководил', 'управлял', 'архитектура', 'стратеги'],
            'lead': ['тимлид', 'руководитель', 'управление', 'менеджер', 'координация']
        }

        # Считаем вес каждого уровня в тексте
        level_weights = {}
        for level, keywords in experience_keywords.items():
            weight = sum(1 for keyword in keywords if keyword in text_lower)
            level_weights[level] = weight

        # Определяем доминирующий уровень
        if not level_weights:
            return 0

        dominant_level = max(level_weights.items(), key=lambda x: x[1])[0]

        # Сравниваем с целевым уровнем
        if dominant_level == target_experience.lower():
            return 100

        # Получаем список уровней для сравнения позиций
        levels = list(experience_keywords.keys())
        try:
            dominant_index = levels.index(dominant_level)
            target_index = levels.index(target_experience.lower())
            level_diff = abs(dominant_index - target_index)

            if level_diff == 1:
                return 70  # Соседний уровень
            else:
                return 30  # Далекий уровень
        except ValueError:
            return 30  # Если уровень не найден

    @staticmethod
    def generate_explanation(semantic, skills, experience):
        """Генерирует понятное объяснение совпадения"""
        explanations = []

        if semantic > 80:
            explanations.append("Отличное смысловое соответствие")
        elif semantic > 60:
            explanations.append("Хорошее смысловое соответствие")
        elif semantic > 40:
            explanations.append("Умеренное смысловое соответствие")
        else:
            explanations.append("Слабое смысловое соответствие")

        if skills > 80:
            explanations.append("высокое совпадение требований")
        elif skills > 60:
            explanations.append("хорошее совпадение требований")

        if experience > 80:
            explanations.append("идеальное соответствие уровня опыта")

        return ". ".join(explanations)

    @staticmethod
    def find_candidates_for_hr(ideal_profile):
        """Умный поиск кандидатов"""
        # Ищем только опубликованные резюме
        applicants = Applicant.objects.filter(is_published=True)
        matches = []

        for applicant in applicants:
            match_result = AIMatcher.match_candidate_with_profile(applicant, ideal_profile)

            if match_result['final_score'] >= ideal_profile.min_match_percentage:
                matches.append({
                    'applicant': applicant,
                    'match_details': match_result,
                    'score': match_result['final_score']
                })

        # Сортируем по смыслу, а не по поверхностным совпадениям
        matches.sort(key=lambda x: x['match_details']['semantic_similarity'], reverse=True)
        top_matches = matches[:ideal_profile.max_candidates]

        # Сохраняем результаты
        for match in top_matches:
            AISearchMatch.objects.create(
                ideal_candidate_profile=ideal_profile,
                matched_applicant=match['applicant'],
                match_percentage=match['score'],
                match_details=match['match_details']
            )

        return top_matches

    @staticmethod
    def find_vacancies_for_applicant(ideal_profile):
        """Умный поиск вакансий"""
        vacancies = Vacancy.objects.filter(status='published')
        matches = []

        for vacancy in vacancies:
            # Аналогичная логика для вакансий
            vacancy_text = f"{vacancy.title} {vacancy.description} {vacancy.requirements}"
            ideal_text = f"{ideal_profile.ideal_position} {ideal_profile.desired_skills}"

            semantic_similarity = AIMatcher.calculate_semantic_similarity(
                vacancy_text, ideal_text
            )

            if semantic_similarity >= ideal_profile.min_match_percentage:
                matches.append({
                    'vacancy': vacancy,
                    'match_details': {
                        'semantic_similarity': semantic_similarity,
                        'final_score': semantic_similarity,
                        'explanation': f"Смысловое соответствие: {semantic_similarity}%"
                    },
                    'score': semantic_similarity
                })

        matches.sort(key=lambda x: x['score'], reverse=True)
        top_matches = matches[:ideal_profile.max_vacancies]

        for match in top_matches:
            AISearchMatch.objects.create(
                ideal_vacancy_profile=ideal_profile,
                matched_vacancy=match['vacancy'],
                match_percentage=match['score'],
                match_details=match['match_details']
            )

        return top_matches