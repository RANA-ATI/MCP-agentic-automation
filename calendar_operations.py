"""
Calendar Operations Module
Contains all the calendar-related operations (add, update, delete meetings)
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

class CalendarOperations:
    """Handles all calendar operations"""
    
    def __init__(self, service):
        """
        Initialize with Google Calendar service
        
        Args:
            service: Authenticated Google Calendar service object
        """
        self.service = service
    
    def parse_datetime(self, date_str: str) -> str:
        """
        Parse various datetime formats to RFC3339 format
        
        Args:
            date_str: Date/time string in various formats
            
        Returns:
            RFC3339 formatted datetime string
            
        Raises:
            ValueError: If the date format is not recognized
        """
        # List of common datetime formats people might use
        formats = [
            '%Y-%m-%d %H:%M',           # 2024-12-25 14:30
            '%Y-%m-%d %H:%M:%S',        # 2024-12-25 14:30:00
            '%m/%d/%Y %H:%M',           # 12/25/2024 14:30
            '%d/%m/%Y %H:%M',           # 25/12/2024 14:30
            '%Y-%m-%dT%H:%M:%S',        # 2024-12-25T14:30:00
            '%Y-%m-%d'                  # 2024-12-25 (date only)
        ]
        
        # Try each format
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.isoformat()
            except ValueError:
                continue
        
        # Try to parse as ISO format (last resort)
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.isoformat()
        except Exception as e:
            raise ValueError(f"Unable to parse datetime: {date_str}. Error: {str(e)}")
    
    def add_meeting(self, 
                   title: str,
                   start_time: str,
                   end_time: str,
                   description: str = "",
                   attendees: List[str] = None,
                   location: str = "",
                   calendar_id: str = "primary") -> Dict[str, Any]:
        """
        Add a new meeting to Google Calendar
        
        Args:
            title: Meeting title/summary
            start_time: Start time (various formats accepted)
            end_time: End time (various formats accepted)
            description: Meeting description (optional)
            attendees: List of attendee email addresses (optional)
            location: Meeting location (optional)
            calendar_id: Calendar ID (default: 'primary')
            
        Returns:
            Dictionary with event details
            
        Raises:
            Exception: If meeting creation fails
        """
        try:
            # Parse the datetime strings
            start_datetime = self.parse_datetime(start_time)
            end_datetime = self.parse_datetime(end_time)
            
            # Create the event object
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': 'UTC',
                },
            }
            
            # Add optional fields if provided
            if location:
                event['location'] = location
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            # Create the event in Google Calendar
            event_result = self.service.events().insert(
                calendarId=calendar_id, 
                body=event
            ).execute()
            
            return {
                'success': True,
                'event_id': event_result['id'],
                'title': title,
                'start_time': start_datetime,
                'end_time': end_datetime,
                'html_link': event_result.get('htmlLink', 'N/A')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_meeting(self, event_id: str, calendar_id: str = "primary") -> Dict[str, Any]:
        """
        Delete a meeting from Google Calendar
        
        Args:
            event_id: ID of the event to delete
            calendar_id: Calendar ID (default: 'primary')
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Delete the event
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            return {
                'success': True,
                'event_id': event_id,
                'message': 'Meeting deleted successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_meeting(self, 
                      event_id: str,
                      title: Optional[str] = None,
                      start_time: Optional[str] = None,
                      end_time: Optional[str] = None,
                      description: Optional[str] = None,
                      attendees: Optional[List[str]] = None,
                      location: Optional[str] = None,
                      calendar_id: str = "primary") -> Dict[str, Any]:
        """
        Update an existing meeting in Google Calendar
        
        Args:
            event_id: ID of the event to update
            title: New meeting title (optional)
            start_time: New start time (optional)
            end_time: New end time (optional)
            description: New description (optional)
            attendees: New list of attendees (optional)
            location: New location (optional)
            calendar_id: Calendar ID (default: 'primary')
            
        Returns:
            Dictionary with operation result
        """
        try:
            # First, get the existing event
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Update fields if new values provided
            if title is not None:
                event['summary'] = title
            
            if start_time is not None:
                start_datetime = self.parse_datetime(start_time)
                event['start']['dateTime'] = start_datetime
            
            if end_time is not None:
                end_datetime = self.parse_datetime(end_time)
                event['end']['dateTime'] = end_datetime
            
            if description is not None:
                event['description'] = description
            
            if location is not None:
                event['location'] = location
            
            if attendees is not None:
                event['attendees'] = [{'email': email} for email in attendees]
            
            # Update the event in Google Calendar
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            return {
                'success': True,
                'event_id': event_id,
                'title': updated_event.get('summary', 'N/A'),
                'html_link': updated_event.get('htmlLink', 'N/A'),
                'message': 'Meeting updated successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_upcoming_events(self, max_results: int = 10, calendar_id: str = "primary") -> Dict[str, Any]:
        """
        Get upcoming events (useful for finding event IDs)
        
        Args:
            max_results: Maximum number of events to return
            calendar_id: Calendar ID (default: 'primary')
            
        Returns:
            Dictionary with events list
        """
        try:
            # Get current time in RFC3339 format
            now = datetime.utcnow().isoformat() + 'Z'
            
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return {
                'success': True,
                'events': events,
                'count': len(events)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }