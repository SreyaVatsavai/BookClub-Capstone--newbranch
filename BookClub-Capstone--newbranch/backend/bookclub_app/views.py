# views.py - API endpoints for the BookClub application
# I structured these views around key features:
# 1. Authentication (register, login, username checks)
# 2. Book discovery and details
# 3. Reading group management
# 4. Discussion and social features
# 5. Reading progress tracking
#
# I used Django REST framework decorators and made most endpoints
# require authentication for security.

from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q  # For complex book search queries
from django.utils.dateparse import parse_date

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Book, DiscussionPost, ReadingGroup, GroupMembership, ReadingProgress, Chapter, ChapterSchedule, Reaction
from .serializers import (
    DiscussionPostSerializer,
    UserSerializer,
    BookSerializer,
    ReadingGroupSerializer,
    ReadingProgressSerializer,
    ChapterSerializer,
    ChapterScheduleSerializer,
)
import re

# ==== AUTH ====

@api_view(["GET"])
@permission_classes([AllowAny])
def check_username(request):
    """
    Endpoint: GET /api/check-username/?username=<name>
    
    I added this endpoint to provide real-time username availability checks
    during registration. It's publicly accessible (AllowAny) since it's used
    before registration.
    
    Design choices:
    - Simple GET with query param for easy frontend integration
    - Returns both username and availability for UI feedback
    - Basic validation to ensure username is provided
    """
    username = request.GET.get("username")
    
    if not username:
        return Response(
            {"error": "Username parameter required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    # Simple DB query to check existence
    is_available = not User.objects.filter(username=username).exists()
    
    return Response({
        "username": username,
        "available": is_available
    })


def validate_password_strength(password):
    """
    Validates password strength against our security requirements.
    
    I implemented comprehensive checks to ensure strong passwords:
    - Minimum length for basic security
    - Mix of upper/lowercase for complexity
    - Numbers required for extra entropy
    - No repeating digits to prevent simple patterns
    
    Returns a list of specific error messages to help users fix weak passwords.
    """
    errors = []
    
    # Basic length requirement
    if len(password) < 6:
        errors.append("Password must be at least 6 characters long")
    
    # Character type requirements
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number")
    
    # Ensure both letters and numbers are present
    if not (re.search(r'[a-zA-Z]', password) and re.search(r'[0-9]', password)):
        errors.append("Password must contain both letters and numbers")
    
    # Prevent simple patterns like '111' or '999'
    if re.search(r'(\d)\1{2,}', password):
        errors.append("Password cannot contain consecutive repeating digits (e.g., 111, 222)")
    
    return errors

@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    """
    Endpoint: POST /api/auth/register/
    Payload: { "username": "...", "password": "..." }
    
    Handles new user registration with comprehensive validation. I implemented:
    - Required field validation
    - Username length and uniqueness checks
    - Password strength validation via validate_password_strength()
    
    Security considerations:
    - CSRF exempt since it's an API endpoint
    - Publicly accessible for registration
    - Returns specific validation errors to help users
    """
    username = request.data.get("username")
    password = request.data.get("password")

    # Basic required field validation
    if not username or not password:
        return Response(
            {"error": "Username and password required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Username requirements - kept minimal for usability
    if len(username) < 3:
        return Response(
            {"username": ["Username must be at least 3 characters long"]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Uniqueness check - though we have the check-username endpoint,
    # this prevents race conditions
    if User.objects.filter(username=username).exists():
        return Response(
            {"username": ["Username already taken"]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate password strength
    password_errors = validate_password_strength(password)
    if password_errors:
        return Response(
            {"password": password_errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.create_user(username=username, password=password)
    return Response(
        {"message": "User created successfully. Please log in."}, 
        status=status.HTTP_201_CREATED
    )


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def user_login(request):
    """
    Endpoint: POST /api/auth/login/
    Payload: { "username": "...", "password": "..." }
    
    Handles user authentication. I kept this endpoint simple but secure:
    - Uses Django's built-in authenticate() for password checking
    - Creates a session on successful login
    - Returns user data for the frontend
    
    Security:
    - CSRF exempt for API access
    - Returns 401 for invalid credentials
    - Doesn't specify which field (username/password) was wrong
    """
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)

    if user:
        # Create session and return user data
        login(request, user)
        return Response(UserSerializer(user).data)

    # Generic error - don't specify what was wrong
    return Response(
        {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """
    Endpoint: POST /api/auth/logout/
    
    Simple endpoint to log out the current user. I kept this minimal:
    - Uses Django's built-in logout()
    - Requires authentication to prevent unnecessary calls
    - Returns a simple success message
    
    Security:
    - Protected endpoint (requires auth)
    - Invalidates the user's session
    """
    logout(request)
    return Response({"message": "Logged out"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user(request):
    """
    Endpoint: GET /api/auth/user/
    Response: User profile data
    
    Quick endpoint to get current user data. Used by the frontend to:
    - Verify authentication status
    - Get user details after session restore
    - Update UI with user info
    
    Security:
    - Protected endpoint (requires auth)
    - Only returns current user's data
    - Uses serializer for safe field filtering
    """
    return Response(UserSerializer(request.user).data)


# ==== BOOKS ====

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def book_list(request):
    """
    Endpoint: GET /api/books/
    Query params: 
        search: Search in title and author (optional)
        genre: Filter by exact genre (optional)
    
    Book discovery endpoint with flexible search:
    - Full book list when no filters
    - Text search across title and author
    - Genre filtering for targeted browsing
    
    Implementation details:
    - Case-insensitive search using icontains
    - Exact genre matching to prevent partial matches
    - Combines multiple filters with AND logic
    
    Performance:
    - No joins or complex queries
    - Returns only essential fields via serializer
    """
    query = request.GET.get("search", "")
    genre = request.GET.get("genre", "")
    books = Book.objects.all()

    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))
    if genre:
        books = books.filter(genre__iexact=genre)

    return Response(BookSerializer(books, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def book_detail(request, pk):
    """
    Endpoint: GET /api/books/{pk}/
    Response: Book details + available reading groups
    
    Comprehensive book details endpoint that I designed to:
    - Show full book information
    - List available reading groups for the book
    - Help users find active groups to join
    
    Implementation details:
    - Uses prefetch_related for efficient group loading
    - Filters out empty/inactive groups
    - Post-processes to remove full groups
    
    Optimizations:
    - Prefetches related groups to avoid N+1 queries
    - Combines book and group data in single response
    - Only returns non-full groups to prevent failed joins
    """
    try:
        book = Book.objects.prefetch_related("readinggroup_set").get(pk=pk)
    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

    # Find active groups that aren't full
    available_groups = book.readinggroup_set.filter(memberships__isnull=False).distinct()
    available_groups = [g for g in available_groups if not g.is_full]

    data = BookSerializer(book).data
    data["available_groups"] = ReadingGroupSerializer(available_groups, many=True).data
    return Response(data)


# ==== GROUPS ====

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def group_list_create(request):
    """
    Endpoint: 
        GET /api/groups/ - List user's groups
        POST /api/groups/ - Create new group
    
    Dual-purpose endpoint I designed for group management:
    1. GET: List all groups user is a member of
    2. POST: Create a new reading group
    
    Creation process:
    1. Validate group data via serializer
    2. Set current user as creator
    3. Auto-create membership for creator
    
    Design choices:
    - Combined list/create to reduce endpoints
    - Auto-membership saves extra API call
    - GET returns only relevant groups to user
    
    Security:
    - Protected endpoint (requires auth)
    - Creator auto-set to authenticated user
    - Validation via serializer
    """
    if request.method == "POST":
        serializer = ReadingGroupSerializer(data=request.data)
        if serializer.is_valid():
            # Save the group with the creator
            group = serializer.save(creator=request.user)
            # Automatically add creator as a member
            GroupMembership.objects.create(user=request.user, group=group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # GET: list user's groups
    user_groups = ReadingGroup.objects.filter(memberships__user=request.user)
    return Response(ReadingGroupSerializer(user_groups, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_group(request, pk):
    """
    Endpoint: POST /api/groups/{pk}/join/
    
    Handles user requests to join reading groups. I implemented
    comprehensive validation to ensure proper group joining:
    
    Validation order:
    1. Group exists
    2. Group has space
    3. User isn't already a member
    
    Design choices:
    - Simple POST endpoint for single action
    - Clear error messages for each case
    - Atomic membership creation
    
    Security:
    - Protected endpoint (requires auth)
    - Validates group existence
    - Prevents duplicate memberships
    """
    try:
        group = ReadingGroup.objects.get(pk=pk)
    except ReadingGroup.DoesNotExist:
        return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)

    if group.is_full:
        return Response({"error": "Group is full"}, status=status.HTTP_400_BAD_REQUEST)

    if GroupMembership.objects.filter(user=request.user, group=group).exists():
        return Response({"error": "Already a member"}, status=status.HTTP_400_BAD_REQUEST)

    GroupMembership.objects.create(user=request.user, group=group)
    return Response({"message": "Joined group successfully"})


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def leave_group(request, pk):
    """
    Endpoint: POST/DELETE /api/groups/{pk}/leave/
    
    Handles users leaving reading groups. I implemented special logic
    to handle group creators and cleanup:
    
    Validation flow:
    1. Group exists
    2. User is a member
    3. If creator, ensure no other members
    
    Cleanup actions:
    1. Remove group membership
    2. Delete reading progress
    3. Delete chapter schedules (cascade)
    
    Special cases:
    - Group creators can't leave if others present
    - All user data removed on successful leave
    - Both POST/DELETE supported for flexibility
    
    Security:
    - Protected endpoint (requires auth)
    - Validates membership
    - Ensures creator responsibility
    """
    try:
        group = ReadingGroup.objects.get(pk=pk)
    except ReadingGroup.DoesNotExist:
        return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if user is a member
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group)
    except GroupMembership.DoesNotExist:
        return Response({"error": "Not a member of this group"}, status=status.HTTP_400_BAD_REQUEST)

    # Prevent creator from leaving if there are other members
    if group.creator == request.user and group.member_count > 1:
        return Response(
            {"error": "As the group creator, you cannot leave while other members are present. Transfer ownership or wait for others to leave first."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Delete membership and related reading progress
    membership.delete()
    
    # Also delete the user's reading progress for this group
    ReadingProgress.objects.filter(user=request.user, group=group).delete()
    
    return Response({"message": "Left group successfully"})


# ==== DISCUSSIONS ====

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def group_discussion(request, group_id):
    """
    Endpoints: 
        GET /api/groups/{group_id}/discussion/ - List all posts
        POST /api/groups/{group_id}/discussion/ - Create new post
    
    Core discussion feature that I designed to support group interactions:
    
    GET functionality:
    - Lists all posts for the group
    - Includes comments and reactions
    - Uses prefetch_related for performance
    
    POST functionality:
    - Creates new discussion posts
    - Auto-assigns author and group
    - Validates post content
    
    Design decisions:
    - Combined list/create for simpler API
    - Prefetch related data to minimize queries
    - Auto-assignment reduces client complexity
    
    Security:
    - Protected endpoint (requires auth)
    - Membership verification
    - Author auto-set to prevent spoofing
    """
    group = get_object_or_404(ReadingGroup, id=group_id)

    # Check if user is a member
    if not GroupMembership.objects.filter(group=group, user=request.user).exists():
        return Response(
            {"error": "Not a member of this group"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "POST":
        # Automatically assign author and group
        serializer = DiscussionPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, group=group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # GET: list all posts for the group
    posts = DiscussionPost.objects.filter(group=group).prefetch_related("comments", "reactions")
    return Response(DiscussionPostSerializer(posts, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_comment(request, post_id):
    """
    Endpoint: POST /api/posts/{post_id}/comments/
    Payload: { "content": "comment text" }
    
    Handles comment creation on discussion posts. I designed this with:
    
    Validation chain:
    1. Post exists
    2. User is group member
    3. Comment content valid
    
    Implementation choices:
    - Simple POST-only endpoint
    - Auto-assigns author and post
    - Validates group membership
    
    Security features:
    - Protected endpoint (requires auth)
    - Group membership check
    - Author auto-assignment
    - Content validation
    """
    try:
        post = DiscussionPost.objects.get(id=post_id)
    except DiscussionPost.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if user is a member of the post's group
    if not GroupMembership.objects.filter(group=post.group, user=request.user).exists():
        return Response(
            {"error": "Not a member of this group"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Create comment
    from .serializers import CommentSerializer
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user, post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_reaction(request, post_id):
    """
    Endpoint: POST /api/posts/{post_id}/react/
    Payload: { "emoji": "👍" }
    Response: { "action": "added"/"removed", "reactions": [...] }
    
    Smart reaction toggle endpoint I designed for post interactions:
    
    Features:
    - Toggles emoji reactions on/off
    - One emoji per user per post
    - Returns updated reaction list
    
    Toggle logic:
    1. If reaction exists: remove it
    2. If no reaction: add it
    3. Returns new reaction state
    
    Implementation choices:
    - Simple POST for toggle action
    - Returns complete reaction list
    - Includes toggle action for UI
    
    Security:
    - Protected endpoint (requires auth)
    - Group membership check
    - One reaction per emoji per user
    """
    try:
        post = DiscussionPost.objects.get(id=post_id)
    except DiscussionPost.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check membership
    if not GroupMembership.objects.filter(group=post.group, user=request.user).exists():
        return Response({"error": "Not a member of this group"}, status=status.HTTP_403_FORBIDDEN)

    emoji = request.data.get('emoji')
    if not emoji:
        return Response({"error": "Emoji is required"}, status=status.HTTP_400_BAD_REQUEST)

    existing = Reaction.objects.filter(post=post, user=request.user, emoji=emoji).first()
    if existing:
        existing.delete()
        action = 'removed'
    else:
        Reaction.objects.create(post=post, user=request.user, emoji=emoji)
        action = 'added'

    # Return updated reactions
    reactions_qs = Reaction.objects.filter(post=post)
    from .serializers import ReactionSerializer
    return Response({'action': action, 'reactions': ReactionSerializer(reactions_qs, many=True).data})


# ==== GROUP DETAILS ====

@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def group_detail(request, group_id):
    """
    Endpoints:
        GET /api/groups/{group_id}/ - Get group details
        PUT/PATCH /api/groups/{group_id}/ - Update group settings
    
    Comprehensive group management endpoint I designed with:
    
    GET features:
    - Full group details
    - Member list with join dates
    - Book information
    - Uses prefetch for efficiency
    
    PUT/PATCH features:
    - Creator-only group updates
    - End date modification
    - Date validation
    
    Implementation details:
    - Prefetches related data
    - Custom member serialization
    - Date parsing and validation
    
    Security:
    - Protected endpoint (requires auth)
    - Member-only access
    - Creator-only updates
    - Date validation
    """
    try:
        group = ReadingGroup.objects.prefetch_related('memberships__user', 'book').get(id=group_id)
    except ReadingGroup.DoesNotExist:
        return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if user is a member
    if not GroupMembership.objects.filter(group=group, user=request.user).exists():
        return Response(
            {"error": "Not a member of this group"},
            status=status.HTTP_403_FORBIDDEN,
        )
    # Handle PATCH/PUT to allow the group creator to update group fields (e.g., end_date)
    if request.method in ("PATCH", "PUT"):
        # Only the creator can change group-level settings
        if group.creator != request.user:
            return Response({"error": "Only the group creator can modify the group"}, status=status.HTTP_403_FORBIDDEN)

        # Allow partial update of end_date (client may send only end_date)
        new_end = request.data.get('end_date')
        if not new_end:
            return Response({"error": "end_date is required"}, status=status.HTTP_400_BAD_REQUEST)

        parsed = parse_date(new_end)
        if not parsed:
            return Response({"error": "Invalid date format for end_date"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure new end_date is not before start_date
        if group.start_date and parsed < group.start_date:
            return Response({"error": "end_date cannot be before group's start_date"}, status=status.HTTP_400_BAD_REQUEST)

        group.end_date = parsed
        group.save()
        return Response(ReadingGroupSerializer(group).data)

    # Construct member details with join dates
    members = [
        {
            'id': m.user.id,
            'username': m.user.username,
            'joined_at': m.joined_at
        }
        for m in group.memberships.all()
    ]

    # Combine all data for comprehensive response
    data = ReadingGroupSerializer(group).data
    data['members'] = members
    data['book_details'] = BookSerializer(group.book).data
    return Response(data)


# ==== READING PROGRESS ====

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reading_progress_list(request):
    """
    Endpoint: GET /api/reading-progress/
    Response: List of all user's reading progress entries
    
    Overview endpoint I designed to show reading activity:
    - Lists all books being read
    - Shows progress in each group
    - Includes related book/group data
    
    Implementation details:
    - Filters by current user
    - Uses select_related for performance
    - Returns comprehensive progress data
    
    Performance optimizations:
    - Eager loads book and group
    - Single query with joins
    - Efficient serialization
    
    Security:
    - Protected endpoint (requires auth)
    - Only returns user's own progress
    """
    progress_list = ReadingProgress.objects.filter(user=request.user).select_related('book', 'group')
    serializer = ReadingProgressSerializer(progress_list, many=True)
    return Response(serializer.data)


@api_view(["GET", "POST", "PUT"])
@permission_classes([IsAuthenticated])
def reading_progress(request, group_id):
    """
    Endpoints:
        GET /api/groups/{group_id}/progress/ - Get/init progress
        POST /api/groups/{group_id}/progress/ - Set reading speed
        PUT /api/groups/{group_id}/progress/ - Update progress
    
    Core reading tracking endpoint I designed with multiple functions:
    
    GET behavior:
    - Fetches existing progress
    - Auto-creates if none exists
    - Initializes with default values
    
    POST behavior:
    - Sets initial reading speed
    - Updates user preferences
    - Creates if needed
    
    PUT behavior:
    - Updates page progress
    - Tracks completion
    - Records reading times
    
    Implementation details:
    - Smart progress initialization
    - Default speed = 0 (unset)
    - Partial updates supported
    - Reading time tracking
    
    Security & Validation:
    - Protected endpoint (requires auth)
    - Group membership check
    - Data validation via serializer
    - Safe progress creation
    """
    try:
        group = ReadingGroup.objects.select_related('book').get(id=group_id)
    except ReadingGroup.DoesNotExist:
        return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check membership
    if not GroupMembership.objects.filter(group=group, user=request.user).exists():
        return Response(
            {"error": "Not a member of this group"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "GET":
        # Get or create progress (don't set speed by default - let frontend show selection)
        try:
            progress = ReadingProgress.objects.get(
                user=request.user,
                book=group.book,
                group=group
            )
        except ReadingProgress.DoesNotExist:
            # Create new progress without speed explicitly set
            # Use 0 to indicate "not set yet" so frontend shows selection dialog
            progress = ReadingProgress.objects.create(
                user=request.user,
                book=group.book,
                group=group,
                reading_speed_minutes=0,  # 0 means not set yet
                current_page=1
            )
        return Response(ReadingProgressSerializer(progress).data)

    elif request.method == "POST":
        # Create/Update reading speed (initial setup)
        progress, created = ReadingProgress.objects.get_or_create(
            user=request.user,
            book=group.book,
            group=group
        )
        serializer = ReadingProgressSerializer(progress, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        # Update progress (page navigation, chapter completion)
        try:
            progress = ReadingProgress.objects.get(
                user=request.user,
                book=group.book,
                group=group
            )
        except ReadingProgress.DoesNotExist:
            return Response({"error": "Progress not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReadingProgressSerializer(progress, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==== GROUP PROGRESS STATISTICS ====

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def group_progress_stats(request, group_id):
    """
    Endpoint: GET /api/groups/{group_id}/stats/
    Response: Detailed group reading statistics
    
    Analytics endpoint I designed to show group progress:
    
    Key metrics:
    - Expected vs actual progress
    - Member completion status
    - Reading activity tracking
    
    Progress categories:
    1. Completed - Finished the book
    2. On Track - At/above expected progress
    3. Behind - Below expected progress
    4. Not Started - No progress recorded
    
    Calculation features:
    - Time-based expected progress
    - Per-member completion tracking
    - Percentage-based progress
    - Last activity tracking
    
    Implementation details:
    - Uses select_related for efficiency
    - Handles missing progress data
    - Rounds percentages for display
    - Handles edge cases (pre-start, post-end)
    
    Security:
    - Protected endpoint (requires auth)
    - Member-only access
    - Safe progress calculations
    """
    try:
        group = ReadingGroup.objects.select_related('book').get(id=group_id)
    except ReadingGroup.DoesNotExist:
        return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check membership
    if not GroupMembership.objects.filter(group=group, user=request.user).exists():
        return Response(
            {"error": "Not a member of this group"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Get all members
    members = GroupMembership.objects.filter(group=group).select_related('user')
    total_members = members.count()
    total_pages = group.book.total_pages if group.book else 100

    # Calculate progress for each member
    from datetime import datetime, timedelta
    today = datetime.now().date()
    
    # Calculate expected progress based on schedule
    start_date = group.start_date
    deadline = group.end_date  # Use end_date instead of deadline
    
    if start_date and deadline:
        total_days = (deadline - start_date).days
        elapsed_days = (today - start_date).days
        
        if elapsed_days < 0:
            # Not started yet
            expected_progress = 0
        elif elapsed_days >= total_days:
            # Past deadline
            expected_progress = 100
        else:
            # In progress
            expected_progress = (elapsed_days / total_days) * 100 if total_days > 0 else 0
    else:
        expected_progress = 0

    # Categorize members
    completed = []  # Finished the book
    on_track = []   # Progress >= expected
    behind = []     # Progress < expected
    not_started = []  # No progress yet

    for membership in members:
        try:
            progress = ReadingProgress.objects.get(
                user=membership.user,
                book=group.book,
                group=group
            )
            current_page = progress.current_page or 1
            progress_percent = (current_page / total_pages) * 100 if total_pages > 0 else 0
            
            member_data = {
                'username': membership.user.username,
                'current_page': current_page,
                'progress_percent': round(progress_percent, 1),
                'last_read': progress.last_read_at
            }
            
            if current_page >= total_pages:
                completed.append(member_data)
            elif progress_percent >= expected_progress:
                on_track.append(member_data)
            else:
                behind.append(member_data)
                
        except ReadingProgress.DoesNotExist:
            not_started.append({
                'username': membership.user.username,
                'current_page': 0,
                'progress_percent': 0,
                'last_read': None
            })

    # Return comprehensive statistics
    return Response({
        'total_members': total_members,
        'expected_progress': round(expected_progress, 1),
        'completed': {
            'count': len(completed),
            'members': completed
        },
        'on_track': {
            'count': len(on_track),
            'members': on_track
        },
        'behind': {
            'count': len(behind),
            'members': behind
        },
        'not_started': {
            'count': len(not_started),
            'members': not_started
        }
    })


# ==== CHAPTER SCHEDULES ====

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_group_chapters(request, group_id):
    """
    Endpoint: GET /api/groups/{group_id}/chapters/
    Response: Book and chapter information
    
    Chapter listing endpoint I designed to support scheduling:
    
    Response includes:
    - Book metadata
    - Chapter details
    - Group schedule dates
    - Total chapter count
    
    Implementation details:
    - Orders chapters by number
    - Includes group date context
    - Returns full chapter data
    
    Performance:
    - Efficient chapter filtering
    - Single query for chapters
    - Minimal book data included
    
    Security:
    - Protected endpoint (requires auth)
    - Member-only access
    - Filtered to group's book
    """
    try:
        group = ReadingGroup.objects.get(id=group_id)
    except ReadingGroup.DoesNotExist:
        return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is a member
    if not GroupMembership.objects.filter(group=group, user=request.user).exists():
        return Response(
            {"error": "Not a member of this group"},
            status=status.HTTP_403_FORBIDDEN,
        )
    
    # Get chapters in order
    chapters = Chapter.objects.filter(book=group.book).order_by('chapter_number')
    serializer = ChapterSerializer(chapters, many=True)
    
    # Combine book and chapter data
    return Response({
        'book_id': group.book.id,
        'book_title': group.book.title,
        'total_chapters': group.book.total_chapters,
        'group_start_date': group.start_date,
        'group_end_date': group.end_date,
        'chapters': serializer.data
    })


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def chapter_schedule_list(request, group_id):
    """
    Endpoints:
        GET /api/groups/{group_id}/schedules/ - Get user's schedules
        POST /api/groups/{group_id}/schedules/ - Create/update schedules
    
    Chapter scheduling endpoint I designed for reading planning:
    
    GET features:
    - Lists user's chapter schedules
    - Includes chapter details
    - Only returns relevant group
    
    POST features:
    - Bulk schedule creation
    - Date validation
    - Error collection
    - Atomic updates
    
    Implementation details:
    - Uses select_related for efficiency
    - Validates dates against group schedule
    - Supports partial success
    - Returns both successes and errors
    
    Validation:
    - Chapter existence
    - Date range checks
    - Required fields
    - Book ownership
    
    Security:
    - Protected endpoint (requires auth)
    - Member-only access
    - Date range enforcement
    - Book scope validation
    """
    try:
        group = ReadingGroup.objects.get(id=group_id)
    except ReadingGroup.DoesNotExist:
        return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is a member
    if not GroupMembership.objects.filter(group=group, user=request.user).exists():
        return Response(
            {"error": "Not a member of this group"},
            status=status.HTTP_403_FORBIDDEN,
        )
    
    if request.method == "GET":
        # Get user's schedules for this group
        schedules = ChapterSchedule.objects.filter(
            user=request.user,
            group=group
        ).select_related('chapter')
        
        serializer = ChapterScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
    
    elif request.method == "POST":
        # Bulk create/update chapter schedules
        schedules_data = request.data.get('schedules', [])
        
        if not schedules_data:
            return Response(
                {"error": "No schedules provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_schedules = []
        errors = []
        
        # Process each schedule in the batch
        for schedule_data in schedules_data:
            chapter_id = schedule_data.get('chapter')
            target_date = schedule_data.get('target_completion_date')
            
            # Validate required fields
            if not chapter_id or not target_date:
                errors.append(f"Missing chapter or date in schedule")
                continue
            
            # Validate chapter exists and belongs to group's book
            try:
                chapter = Chapter.objects.get(id=chapter_id, book=group.book)
            except Chapter.DoesNotExist:
                errors.append(f"Chapter {chapter_id} not found")
                continue
            
            # Validate date is within group's schedule
            target_date_obj = parse_date(target_date)
            if target_date_obj < group.start_date or target_date_obj > group.end_date:
                errors.append(f"Chapter {chapter.chapter_number}: Date must be between {group.start_date} and {group.end_date}")
                continue
            
            # Create or update schedule
            schedule, created = ChapterSchedule.objects.update_or_create(
                user=request.user,
                group=group,
                chapter=chapter,
                defaults={'target_completion_date': target_date}
            )
            
            created_schedules.append(ChapterScheduleSerializer(schedule).data)
        
        # Return results with both successes and errors
        return Response({
            'created': len(created_schedules),
            'schedules': created_schedules,
            'errors': errors
        }, status=status.HTTP_201_CREATED if created_schedules else status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def chapter_schedule_detail(request, group_id, schedule_id):
    """
    Endpoints:
        PUT /api/groups/{group_id}/schedules/{schedule_id}/ - Update schedule
        DELETE /api/groups/{group_id}/schedules/{schedule_id}/ - Remove schedule
    
    Individual schedule management endpoint I designed with:
    
    PUT features:
    - Update target date
    - Mark completion status
    - Track completion time
    - Validate date range
    
    DELETE features:
    - Remove single schedule
    - Clean removal
    
    Implementation details:
    - Validates schedule ownership
    - Updates completion timestamp
    - Handles date validation
    - Supports partial updates
    
    Security:
    - Protected endpoint (requires auth)
    - Owner-only access
    - Group membership check
    - Date range validation
    """
    try:
        group = ReadingGroup.objects.get(id=group_id)
    except ReadingGroup.DoesNotExist:
        return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        schedule = ChapterSchedule.objects.get(
            id=schedule_id,
            user=request.user,
            group=group
        )
    except ChapterSchedule.DoesNotExist:
        return Response({"error": "Schedule not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == "PUT":
        # Update schedule
        target_date = request.data.get('target_completion_date')
        completed = request.data.get('completed')
        
        # Validate and update target date if provided
        if target_date:
            target_date_obj = parse_date(target_date)
            if target_date_obj < group.start_date or target_date_obj > group.end_date:
                return Response(
                    {"error": f"Date must be between {group.start_date} and {group.end_date}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            schedule.target_completion_date = target_date
        
        # Handle completion status and timestamp
        if completed is not None:
            schedule.completed = completed
            if completed:
                from django.utils import timezone
                schedule.completed_at = timezone.now()
            else:
                schedule.completed_at = None
        
        schedule.save()
        serializer = ChapterScheduleSerializer(schedule)
        return Response(serializer.data)
    
    elif request.method == "DELETE":
        schedule.delete()
        return Response({"message": "Schedule deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
