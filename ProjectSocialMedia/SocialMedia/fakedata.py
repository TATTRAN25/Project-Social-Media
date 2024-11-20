from django.contrib.auth.models import User
from SocialMedia.models import UserProfileInfo, Post, Page, Group, GroupMemberShip
from faker import Faker
import random

fake = Faker()

# Tạo nhóm cho người dùng
def create_groups(users, num_groups=3):
    groups = []
    for user in users:
        for _ in range(num_groups):
            group = Group.objects.create(
                name=fake.company(),
                description=fake.text(),
                creator=user,
                is_private=random.choice([True, False])
            )
            groups.append(group)
            # Thêm người dùng vào nhóm
            group.members.add(user)  # Thêm người tạo nhóm làm thành viên
            # Thêm ngẫu nhiên một số thành viên khác vào nhóm
            other_members = [u for u in users if u != user]
            for _ in range(random.randint(1, 5)):  # Thêm từ 1 đến 5 thành viên ngẫu nhiên
                if other_members:
                    member = random.choice(other_members)
                    group.members.add(member)
                    other_members.remove(member)  # Đảm bảo không thêm lại cùng một thành viên
    return groups

# Tạo người dùng mẫu
def create_users(num_users=10):
    users = []
    for _ in range(num_users):
        username = fake.user_name()
        email = fake.email()
        password = fake.password()
        
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfileInfo.objects.create(
            user=user,
            address=fake.address(),
            bio=fake.sentence(),
            status=random.choice(['active', 'inactive', 'banned'])
        )
        users.append(user)
    return users

# Tạo trang cho bài viết
def create_pages(users, num_pages=5):
    pages = []
    for user in users:
        for _ in range(num_pages):
            page = Page.objects.create(
                title=fake.company(),
                content=fake.text(),
                author=user
            )
            pages.append(page)
    return pages

# Tạo bài viết cho mỗi trang
def create_posts(pages, num_posts=3):
    for page in pages:
        for _ in range(num_posts):
            Post.objects.create(
                page=page,
                title=fake.sentence(),
                content=fake.text(),
                author=page.author,
                view_mode=random.choice(['public', 'private', 'only_me'])
            )

# Chạy các hàm để tạo dữ liệu
users = create_users(10)  # Tạo 10 người dùng
pages = create_pages(users, 2)  # Mỗi người dùng tạo 2 trang
groups = create_groups(users, 3)
create_posts(pages, 3)  # Mỗi trang tạo 3 bài viết