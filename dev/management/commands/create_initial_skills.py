from django.core.management.base import BaseCommand
from dev.models import Skill

class Command(BaseCommand):
    help = 'Creates initial skills'

    def handle(self, *args, **kwargs):
        initial_skills = [
            'Python', 'JavaScript', 'React', 'Django',
            'Node.js', 'HTML', 'CSS', 'Vue.js',
            'Angular', 'TypeScript', 'PHP', 'Laravel',
            'Ruby', 'Ruby on Rails', 'Java', 'Spring Boot',
            'C#', '.NET', 'SQL', 'PostgreSQL',
            'MongoDB', 'AWS', 'Docker', 'Kubernetes',
            'Git', 'DevOps', 'Flutter', 'React Native'
        ]

        for skill_name in initial_skills:
            Skill.objects.get_or_create(name=skill_name)
            self.stdout.write(self.style.SUCCESS(f'Created skill: {skill_name}')) 