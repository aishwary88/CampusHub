# CampusHub - Product Requirements Document (PRD)

## Project Overview

CampusHub is a college-exclusive social networking and community platform built for MITS Gwalior.

The platform connects students, faculty, clubs, societies, and administrators through social feeds, events, resources, opportunities, and community engagement.

CampusHub combines the best aspects of social media, club management systems, event management platforms, and professional networking into a single ecosystem.

---

# Problem Statement

Students currently use multiple platforms for different activities:

* WhatsApp Groups
* Instagram Pages
* LinkedIn
* Google Drive
* College Notice Boards
* Google Forms

CampusHub centralizes all these activities into one platform.

---

# Authentication System

## Student Login

Allowed Domain:

@mitsgwl.ac.in

Features:

* Email Verification
* OTP Verification
* Verified Student Status

Role Assigned:

STUDENT

---

## Faculty Login

Allowed Domain:

@mitsgwalior.in

Features:

* Email Verification
* OTP Verification
* Faculty Verification

Role Assigned:

FACULTY

---

## Admin Login

Restricted Login

Only approved administrators can access the admin panel.

Role Assigned:

ADMIN

---

# User Roles

## Student

Permissions:

* Create Posts
* Like Posts
* Comment on Posts
* Reshare Posts
* Save Posts
* Follow Users
* Follow Clubs
* Create Stories
* Upload Resources
* Register for Events
* Apply for Club Membership

---

## Faculty

Permissions:

* Create Official Posts
* Create Events
* Create Stories
* Publish Announcements

Faculty content receives higher feed priority.

---

## Club President

Permissions:

* Manage Club
* Create Club Posts
* Create Club Events
* Create Club Stories
* Approve Membership Requests
* Assign Core Members
* Create Recruitment Posts

---

## Core Member

Permissions:

* Create Club Posts
* Create Club Events
* Approve Member Requests
* Assist Club Management

---

## Admin

Permissions:

* Approve Clubs
* Manage Users
* Manage Events
* Remove Content
* Review Reports
* Assign Roles
* Moderate Platform

---

# Profile System

Each User Profile Contains:

* Name
* Profile Photo
* Branch
* Year
* Roll Number
* Bio
* Skills
* Achievements
* Followers Count
* Following Count
* Campus Score

---

# Badge System

## Role Badges

* VERIFIED STUDENT
* VERIFIED FACULTY
* CLUB PRESIDENT
* CORE MEMBER
* CAMPUSHUB ADMIN
* OFFICIAL MITS CLUB

---

## Achievement Badges

* HACKATHON WINNER
* OPEN SOURCE CONTRIBUTOR
* RESEARCH AUTHOR
* EVENT ORGANIZER
* PLACED STUDENT
* FOUNDER
* TOP CONTRIBUTOR

---

# Social Features

## Posts

Supported Types:

* Student Post
* Club Post
* Event Post
* Resource Post
* Official Notice
* Opportunity Post

Post Actions:

* Like
* Comment
* Reshare
* Save
* Report

---

## Follow System

Features:

* Follow Users
* Unfollow Users
* Followers
* Following

Private Accounts:

* Follow Request
* Accept Request
* Reject Request

---

## Feed System

### Following Feed

Shows:

* Followed Users
* Followed Clubs
* Official Notices

### Explore Feed

Shows:

* Public Posts
* Trending Posts
* Official Posts
* Recommended Content

---

## Feed Priority

Priority Order:

1. Admin Posts
2. Faculty Posts
3. Club Posts
4. Student Posts

---

## Feed Score

Calculated Using:

* Likes
* Comments
* Reshares
* Recency
* Priority Bonus

Used For:

* Recommendations
* Trending Posts
* Explore Feed Ranking

---

# Stories System

Story Duration:

24 Hours

Who Can Create:

* Students
* Faculty
* Clubs

Story Features:

* Story Views
* Story Reactions
* Story Expiry
* Story Analytics

Priority:

1. Faculty Stories
2. Club Stories
3. Following User Stories

---

# Club Management System

## Club Creation

Flow:

Student Request
→ Admin Review
→ Approval
→ Club Created

---

## Club Hierarchy

Admin
→ President
→ Core Members
→ Members
→ Followers

---

## Club Followers

Any student can:

* View Club
* Follow Club
* View Posts
* View Events
* View Resources

No approval required.

---

## Club Membership

Flow:

Membership Request
→ President/Core Member Review
→ Accept or Reject

Approved users receive Member status.

---

## Club Recruitment

Features:

* Recruitment Posts
* Applications
* Application Review
* Selection Workflow

---

# Events System

Who Can Create Events:

* Admin
* Faculty
* Club President
* Core Members

Students Can:

* View Events
* Register
* Save Events

---

## Event Lifecycle

Event
→ Registration
→ Attendance
→ Certificates
→ Gallery

---

# Resource Sharing System

Supported Resources:

* Notes
* PDFs
* Previous Year Papers
* Study Materials
* Roadmaps

Features:

* Upload
* Download
* Save
* Upvote

---

# Opportunity Hub

Categories:

* Internships
* Hackathons
* Scholarships
* Competitions
* Open Source Programs
* Research Opportunities

---

# Trending System

## Trending Clubs

Based On:

* Followers
* Engagement
* Event Activity

---

## Trending Events

Based On:

* Registrations
* Views
* Shares

---

## Trending Posts

Based On:

* Feed Score
* Engagement
* Recency

---

# Campus Score System

Users gain score through:

* Posting
* Event Participation
* Resource Uploads
* Club Contributions
* Engagement

Used For:

* Leaderboards
* Top Contributors
* Reputation

---

# Search System

Search:

* Students
* Faculty
* Clubs
* Events
* Resources
* Opportunities
* Posts

---

# Notifications

Notification Types:

* New Follower
* Follow Request
* Request Accepted
* Post Like
* Post Comment
* Post Reshare
* Club Membership Approved
* Event Reminder
* Club Recruitment Update

---

# Reports & Moderation

Users can report:

* Posts
* Comments
* Users
* Clubs

Admin reviews all reports.

---

# Admin Dashboard

Features:

* Club Approval
* User Management
* Report Management
* Event Management
* Role Assignment
* Content Moderation

---

# Future Features (Phase 2+)

* Real-Time Chat
* Real-Time Notifications
* AI Moderation
* AI Recommendations
* Smart Search
* Recommendation Feed
* Microservices Architecture
* Analytics Dashboard

---

# Proposed Tech Stack

Frontend:

* React
* TypeScript
* Tailwind CSS

Backend:

* FastAPI
* SQLAlchemy

Database:

* PostgreSQL

Authentication:

* JWT
* OTP Verification

Storage:

* Cloudinary

Deployment:

* Render / Railway

Version:
CampusHub v1.0
