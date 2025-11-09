// src/components/layout/NavBar.js
import React, { useState, useEffect } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Divider,
  ListItemText,
  Alert,
} from "@mui/material";
import NotificationsIcon from "@mui/icons-material/Notifications";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";
import api from "../../api/axiosConfig";

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const open = Boolean(anchorEl);

  // Fetch notifications (smart reminders)
  useEffect(() => {
    const fetchNotifications = async () => {
      if (!user) return;

      try {
        const [groupRes, progressRes] = await Promise.all([
          api.get("/groups/"),
          api.get("/reading-progress/"),
        ]);

        // Create a map of group_id to progress
        const progressMap = {};
        progressRes.data.forEach((p) => {
          progressMap[p.group] = p;
        });

        // Generate smart reminders
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const newNotifications = groupRes.data
          .map((group) => {
            const startDate = new Date(group.start_date);
            startDate.setHours(0, 0, 0, 0);
            const deadline = new Date(group.deadline || group.end_date);
            deadline.setHours(0, 0, 0, 0);

            const totalDays = Math.max(
              1,
              (deadline - startDate) / (1000 * 60 * 60 * 24)
            );
            const elapsedDays = (today - startDate) / (1000 * 60 * 60 * 24);
            const daysRemaining = (deadline - today) / (1000 * 60 * 60 * 24);

            const progress = progressMap[group.id];
            const currentProgress = progress ? progress.percentage : 0;

            // Calculate expected progress
            let scheduleProgress = 0;
            if (elapsedDays < 0) {
              scheduleProgress = 0;
            } else if (elapsedDays > totalDays) {
              scheduleProgress = 100;
            } else {
              scheduleProgress = (elapsedDays / totalDays) * 100;
            }

            // Generate different types of notifications
            const reminders = [];

            // 1. Urgent - Deadline approaching (within 3 days)
            if (
              daysRemaining > 0 &&
              daysRemaining <= 3 &&
              currentProgress < 100
            ) {
              reminders.push({
                groupId: group.id,
                type: "urgent",
                severity: "error",
                message: `🚨 Deadline for "${group.name}" is in ${Math.ceil(
                  daysRemaining
                )} day(s)! You're at ${currentProgress}%.`,
              });
            }

            // 2. Overdue - Past deadline
            else if (daysRemaining < 0 && currentProgress < 100) {
              reminders.push({
                groupId: group.id,
                type: "overdue",
                severity: "error",
                message: `📕 "${group.name}" deadline has passed! You're at ${currentProgress}%.`,
              });
            }

            // 3. Behind schedule (more than 15% behind)
            else if (
              elapsedDays > 0 &&
              scheduleProgress > currentProgress + 15
            ) {
              reminders.push({
                groupId: group.id,
                type: "behind",
                severity: "warning",
                message: `⚠️ You're falling behind in "${
                  group.name
                }"! At ${currentProgress}% but should be at ${Math.round(
                  scheduleProgress
                )}%.`,
              });
            }

            // 4. Warning - Slightly behind schedule (5-15% behind)
            else if (
              elapsedDays > 0 &&
              scheduleProgress > currentProgress + 5 &&
              daysRemaining <= 7
            ) {
              reminders.push({
                groupId: group.id,
                type: "warning",
                severity: "info",
                message: `💡 "${
                  group.name
                }": ${currentProgress}% complete with ${Math.ceil(
                  daysRemaining
                )} days left.`,
              });
            }

            // 5. Success - On track
            else if (
              elapsedDays > 0 &&
              currentProgress >= scheduleProgress &&
              currentProgress > 0 &&
              currentProgress < 100 &&
              daysRemaining > 3
            ) {
              reminders.push({
                groupId: group.id,
                type: "success",
                severity: "success",
                message: `✨ Great job! You're ${currentProgress}% through "${group.name}" and on schedule!`,
              });
            }

            return reminders;
          })
          .flat()
          .filter(Boolean);

        // Add some dummy notifications for demonstration
        const dummyNotifications = [
          {
            groupId: null,
            type: "new_member",
            severity: "info",
            message:
              '👥 New member "sarah" joined "To Kill a Mockingbird Discussion Group"!',
          },
          {
            groupId: null,
            type: "new_post",
            severity: "info",
            message:
              '💬 New discussion post in "1984 Book Club": "What did you think about the ending?"',
          },
          {
            groupId: null,
            type: "milestone",
            severity: "success",
            message:
              '🎉 Congratulations! You completed 50% of "The Great Gatsby"!',
          },
          {
            groupId: null,
            type: "comment",
            severity: "info",
            message:
              '💭 john replied to your post in "Pride and Prejudice" discussion.',
          },
          {
            groupId: null,
            type: "achievement",
            severity: "success",
            message: "🏆 Achievement unlocked: Read 3 books this month!",
          },
        ];

        // Combine smart reminders with dummy notifications
        const allNotifications = [...newNotifications, ...dummyNotifications];
        setNotifications(allNotifications);
      } catch (err) {
        console.error("Failed to load notifications", err);
        // Show dummy notifications even if API fails
        const dummyNotifications = [
          {
            groupId: null,
            type: "new_member",
            severity: "info",
            message:
              '👥 New member "sarah" joined "To Kill a Mockingbird Discussion Group"!',
          },
          {
            groupId: null,
            type: "new_post",
            severity: "info",
            message:
              '💬 New discussion post in "1984 Book Club": "What did you think about the ending?"',
          },
          {
            groupId: null,
            type: "milestone",
            severity: "success",
            message:
              '🎉 Congratulations! You completed 50% of "The Great Gatsby"!',
          },
          {
            groupId: null,
            type: "comment",
            severity: "info",
            message:
              '💭 john replied to your post in "Pride and Prejudice" discussion.',
          },
          {
            groupId: null,
            type: "achievement",
            severity: "success",
            message: "🏆 Achievement unlocked: Read 3 books this month!",
          },
          {
            groupId: null,
            type: "reminder",
            severity: "warning",
            message: "📖 Don't forget to update your reading progress today!",
          },
        ];
        setNotifications(dummyNotifications);
      }
    };

    fetchNotifications();
    // Refresh notifications every 5 minutes
    const interval = setInterval(fetchNotifications, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [user]);

  const handleNotificationClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleNotificationClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationItemClick = (groupId) => {
    handleNotificationClose();
    if (groupId) {
      navigate(`/groups/${groupId}`);
    }
    // For dummy notifications without groupId, just close the menu
  };

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <AppBar
      position="static"
      sx={{
        bgcolor: "rgba(128, 128, 128, 0.3)", // Transparent grey
        backdropFilter: "blur(10px)",
        color: "white", // White text
      }}
    >
      <Toolbar>
        <Typography
          variant="h6"
          sx={{
            flexGrow: 1,
            cursor: "pointer",
            color: "white", // White text
            fontWeight: "bold",
          }}
          onClick={() => navigate("/home")}
        >
          Group Book Reading
        </Typography>
        {user ? (
          <Box sx={{ display: "flex", alignItems: "center" }}>
            {/* Notification Icon */}
            <IconButton
              color="inherit"
              onClick={handleNotificationClick}
              sx={{ mr: 2 }}
              aria-label="notifications"
            >
              <Badge badgeContent={notifications.length} color="error">
                <NotificationsIcon sx={{ color: "white" }} />
              </Badge>
            </IconButton>

            {/* Notification Dropdown Menu */}
            <Menu
              anchorEl={anchorEl}
              open={open}
              onClose={handleNotificationClose}
              PaperProps={{
                sx: {
                  bgcolor: "rgba(128, 128, 128, 0.9)", // Darker grey for dropdown
                  color: "white", // White text in dropdown
                  maxWidth: 400,
                  maxHeight: 500,
                  mt: 1,
                },
              }}
              transformOrigin={{ horizontal: "right", vertical: "top" }}
              anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
            >
              <Box sx={{ px: 2, py: 1 }}>
                <Typography
                  variant="h6"
                  sx={{ fontWeight: "bold", color: "white" }}
                >
                  📬 Notifications
                </Typography>
              </Box>
              <Divider sx={{ bgcolor: "rgba(255,255,255,0.3)" }} />

              {notifications.length === 0 ? (
                <MenuItem disabled sx={{ color: "rgba(255,255,255,0.7)" }}>
                  <ListItemText
                    primary="No notifications"
                    secondary="You're all caught up! 🎉"
                    primaryTypographyProps={{
                      sx: { color: "rgba(255,255,255,0.7)" },
                    }}
                    secondaryTypographyProps={{
                      sx: { color: "rgba(255,255,255,0.5)" },
                    }}
                  />
                </MenuItem>
              ) : (
                notifications.map((notification, index) => (
                  <React.Fragment key={index}>
                    <MenuItem
                      onClick={() =>
                        handleNotificationItemClick(notification.groupId)
                      }
                      sx={{
                        whiteSpace: "normal",
                        py: 1.5,
                        "&:hover": {
                          backgroundColor: "rgba(255,255,255,0.1)",
                        },
                      }}
                    >
                      <Alert
                        severity={notification.severity}
                        sx={{
                          width: "100%",
                          "& .MuiAlert-message": {
                            width: "100%",
                            color: "white",
                          },
                          "& .MuiAlert-action": {
                            color: "white",
                          },
                          // Black background for better visibility
                          bgcolor:
                            notification.severity === "error"
                              ? "rgba(0, 0, 0, 0.8)"
                              : notification.severity === "warning"
                              ? "rgba(0, 0, 0, 0.8)"
                              : notification.severity === "info"
                              ? "rgba(0, 0, 0, 0.8)"
                              : "rgba(0, 0, 0, 0.8)",
                          // Enhanced text colors for better contrast
                          color:
                            notification.severity === "error"
                              ? "#f44336"
                              : notification.severity === "warning"
                              ? "#ff9800"
                              : notification.severity === "info"
                              ? "#2196f3"
                              : "#4caf50",
                          // Enhanced icon color
                          "& .MuiAlert-icon": {
                            color:
                              notification.severity === "error"
                                ? "#f44336"
                                : notification.severity === "warning"
                                ? "#ff9800"
                                : notification.severity === "info"
                                ? "#2196f3"
                                : "#4caf50",
                          },
                        }}
                      >
                        {notification.message}
                      </Alert>
                    </MenuItem>
                    {index < notifications.length - 1 && (
                      <Divider sx={{ bgcolor: "rgba(255,255,255,0.1)" }} />
                    )}
                  </React.Fragment>
                ))
              )}
            </Menu>

            <Typography
              variant="body1"
              sx={{
                display: "inline",
                mr: 2,
                color: "white", // White text
              }}
            >
              Welcome, {user.username}!
            </Typography>
            <Button
              color="inherit"
              onClick={handleLogout}
              sx={{
                color: "white", // White text
                "&:hover": {
                  backgroundColor: "rgba(255,255,255,0.1)",
                },
              }}
            >
              Logout
            </Button>
          </Box>
        ) : (
          <>
            <Button
              color="inherit"
              href="/register"
              sx={{
                color: "white", // White text
                "&:hover": {
                  backgroundColor: "rgba(255,255,255,0.1)",
                },
              }}
            >
              Sign Up
            </Button>
            <Button
              color="inherit"
              href="/login"
              sx={{
                color: "white", // White text
                "&:hover": {
                  backgroundColor: "rgba(255,255,255,0.1)",
                },
              }}
            >
              Login
            </Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
}
