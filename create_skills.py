from workers.models import Skill

skills = ['Masonry', 'Carpentry', 'Plumbing', 'Electrical', 'Painting', 'Welding', 'Tiling', 'Flooring', 'Roofing']

for skill_name in skills:
    Skill.objects.get_or_create(name=skill_name)

print('Skills created successfully')
