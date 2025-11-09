# models.py - Core data models for the BookClub application
# I structured these models to support a social reading experience where users can:
# - Join reading groups for specific books
# - Track their reading progress
# - Participate in chapter-based discussions
# - Set and follow personal reading schedules

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Book(models.Model):
    """
    Represents a book in our application. I kept the model focused on essential
    reading group features but made it extensible for future enhancements.
    
    Key features I included:
    - Basic book metadata (title, author, genre)
    - Page and chapter counts for progress tracking
    - Optional cover image for better UX
    """
    # Core book information
    title = models.CharField(max_length=200)  # Most titles fit within 200 chars
    author = models.CharField(max_length=255)  # Author name(s)
    genre = models.CharField(max_length=100)  # Main genre for filtering
    description = models.TextField()  # Full book description/synopsis
    # These fields help calculate reading progress and schedules
    total_pages = models.PositiveIntegerField()
    total_chapters = models.PositiveIntegerField()
    # URL to book cover - made optional since not all books might have covers
    cover_image = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.title

class Chapter(models.Model):
    """
    Represents individual chapters in a book. I added this to:
    - Enable chapter-by-chapter discussions
    - Support granular reading progress tracking
    - Allow chapter-based scheduling in reading groups
    """
    # Link to the associated book
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters')
    chapter_number = models.PositiveIntegerField()  # For ordering and progress tracking
    title = models.CharField(max_length=255)  # Chapter title if available

    class Meta:
        # Always show chapters in numerical order
        ordering = ['chapter_number']

class ReadingGroup(models.Model):
    """
    Core model for the social reading feature. Each group:
    - Focuses on one specific book
    - Has a creator who manages the group
    - Runs for a defined period (start_date to end_date)
    - Limited to 10 members for meaningful discussions
    
    I implemented properties to handle member limits and counts
    to keep the business logic centralized.
    """
    name = models.CharField(max_length=255)  # Group name chosen by creator
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    # Date range for the reading schedule
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def member_count(self):
        """
        I made this a property to always get accurate counts
        and avoid storing redundant data
        """
        return self.memberships.count()

    @property
    def is_full(self):
        """
        Enforces the 10-member limit I set for optimal group size.
        Used in views to prevent joining full groups.
        """
        return self.member_count >= 10

    def __str__(self):
        return f"{self.name} ({self.book.title})"

class GroupMembership(models.Model):
    """
    Tracks group membership with a many-to-many relationship between
    Users and ReadingGroups. I added joined_at for activity tracking
    and potential future features (e.g., member milestones).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ReadingGroup, on_delete=models.CASCADE, related_name='memberships')
    joined_at = models.DateTimeField(auto_now_add=True)  # Timestamp when user joined

    class Meta:
        # Prevent duplicate memberships - a user can only join a group once
        unique_together = ('user', 'group')

class DiscussionPost(models.Model):
    """
    Handles group discussions about the book. I designed this to support:
    - General book discussions
    - Chapter-specific discussions (optional chapter field)
    - Threaded comments
    - Emoji reactions for engagement
    
    The chapter field is optional so members can discuss both specific
    chapters and general book topics.
    """
    # Each post belongs to a specific reading group
    group = models.ForeignKey(ReadingGroup, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # Optional link to specific chapter - allows both chapter-specific and general discussion
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()  # The actual discussion post content
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    """
    Represents replies to discussion posts. I kept this simple but effective:
    - Links to parent post
    - Tracks author and timestamp
    - Just needs content (no extra features needed yet)
    
    I decided against nested comments to keep the discussion flow cleaner.
    """
    post = models.ForeignKey(DiscussionPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()  # The comment text
    created_at = models.DateTimeField(auto_now_add=True)

class Reaction(models.Model):
    """
    Adds emoji reactions to discussion posts. I implemented this to:
    - Make discussions more engaging
    - Allow quick feedback without full comments
    - Track who reacted with what emoji
    
    The unique_together constraint ensures a user can't add the same
    emoji reaction multiple times to a post.
    """
    post = models.ForeignKey(DiscussionPost, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Store emoji as text - kept length=10 since most emoji are 1-2 chars
    emoji = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent duplicate reactions - one emoji type per user per post
        unique_together = ('post', 'user', 'emoji')

    def __str__(self):
        return f"{self.user.username} reacted {self.emoji} on post {self.post.id}"
class ReadingProgress(models.Model):
    """
    Tracks individual reading progress for users. I designed this to support:
    - Page-level progress tracking
    - Reading speed preferences
    - Chapter completion status
    - Group-specific progress (optional group field)
    
    The reading_speed_minutes helps calculate estimated completion times
    and suggest schedules. I made the group field optional so users can
    track progress even outside of groups.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    # Optional group link - allows progress tracking outside groups too
    group = models.ForeignKey(ReadingGroup, on_delete=models.CASCADE, null=True, blank=True)
    
    # User's reading pace - used for schedule suggestions
    reading_speed_minutes = models.IntegerField(default=1, help_text='Minutes per page')
    
    # Current progress tracking
    current_page = models.IntegerField(default=1)
    current_chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True)
    chapter_deadline = models.DateField(null=True, blank=True)
    chapter_status = models.CharField(
        max_length=20,
        choices=[('in_progress', 'In Progress'), ('completed', 'Completed')],
        default='in_progress'
    )
    
    # Timestamps for activity tracking
    last_read_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user can only have one progress record per book-group combination
        unique_together = ('user', 'book', 'group')

class ChapterSchedule(models.Model):
    """
    Manages personal chapter completion schedules. I added this to:
    - Let users set their own pace within the group timeframe
    - Track individual chapter completion
    - Show schedule adherence in group stats
    
    I made schedules group-specific since different groups might
    read the same book at different paces.
    """
    # Core relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ReadingGroup, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    
    # Schedule and completion tracking
    target_completion_date = models.DateField()  # When user plans to finish the chapter
    completed = models.BooleanField(default=False)  # Quick completion status
    completed_at = models.DateTimeField(null=True, blank=True)  # When actually completed
    
    # Audit timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Track schedule adjustments

    class Meta:
        # One schedule entry per chapter per user in a group
        unique_together = ('user', 'group', 'chapter')
        # Show chapters in reading order
        ordering = ['chapter__chapter_number']

    def __str__(self):
        return f"{self.user.username} - {self.chapter.title} - {self.target_completion_date}"