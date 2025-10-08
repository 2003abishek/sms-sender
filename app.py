import streamlit as st
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
import io

# Haversine formula to calculate distance between two coordinates
def calculate_distance(lat1, lon1, lat2, lon2):
    # Earth radius in kilometers
    R = 6371.0
    
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return distance

# Function to process CSV and calculate distances
def process_locations_csv(csv_file, reference_lat, reference_lon):
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Clean column names (remove quotes and whitespace)
        df.columns = df.columns.str.replace('"', '').str.strip()
        
        # Convert latitude and longitude to numeric
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        
        # Drop rows with invalid coordinates
        df = df.dropna(subset=['Latitude', 'Longitude'])
        
        # Calculate distance for each location
        df['Distance_km'] = df.apply(
            lambda row: calculate_distance(
                reference_lat, reference_lon, 
                row['Latitude'], row['Longitude']
            ), axis=1
        )
        
        # Sort by distance
        df = df.sort_values('Distance_km')
        
        # Add distance order starting from 0
        df['Distance_Order'] = range(len(df))
        
        return df
        
    except Exception as e:
        st.error(f"Error processing CSV file: {str(e)}")
        return None

# Function to find users close to the last registered user
def find_nearby_users(df, max_distance_km=10):
    if df is None or df.empty:
        return None, None, None
    
    # Find the last registered user (assuming the last row is the most recent)
    last_user = df.iloc[-1]
    last_user_coords = (last_user['Latitude'], last_user['Longitude'])
    
    # Calculate distance from last user to all other users
    df['Distance_From_Last_User_km'] = df.apply(
        lambda row: calculate_distance(
            last_user_coords[0], last_user_coords[1],
            row['Latitude'], row['Longitude']
        ), axis=1
    )
    
    # Find users within the specified distance (excluding the last user itself)
    nearby_users = df[df['Distance_From_Last_User_km'] <= max_distance_km]
    nearby_users = nearby_users[nearby_users['Distance_From_Last_User_km'] > 0]  # Exclude self
    
    return last_user, nearby_users, last_user_coords

# Function to prepare dataframe for mapping
def prepare_for_mapping(df):
    """Convert column names to Streamlit map compatible format"""
    map_df = df.copy()
    
    # Rename columns to Streamlit's expected names
    column_mapping = {
        'Latitude': 'lat',
        'Longitude': 'lon',
        'LAT': 'lat',
        'LONG': 'lon',
        'latitude': 'lat', 
        'longitude': 'lon'
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in map_df.columns:
            map_df = map_df.rename(columns={old_col: new_col})
    
    return map_df

# SMS sharing functionality (moved to top)
def sms_sharer():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📲 Share App Link")
    
    # Updated with your actual URL
    app_url = "https://app1-pkgk.onrender.com/"
    
    st.sidebar.write("**App Link:**")
    st.sidebar.code(app_url)
    
    st.sidebar.subheader("Quick Share:")
    phone = st.sidebar.text_input("Enter phone number:", key="phone")
    
    if phone:
        message = f"Check out this location sharing app: {app_url}"
        sms_url = f"sms:{phone}?body={message}"
        
        st.sidebar.markdown(
            f'<a href="{sms_url}" target="_blank">'
            '<button style="background-color:green;color:white;padding:10px;border:none;border-radius:5px;">'
            'Send SMS</button></a>', 
            unsafe_allow_html=True
        )
    
    st.sidebar.info("💡 The SMS button will open your phone's messaging app with the link pre-filled.")

# Main Streamlit app
def main():
    st.set_page_config(
        page_title="Location Distance Calculator",
        page_icon="📍",
        layout="wide"
    )
    
    # Display SMS sharer in sidebar at the top
    sms_sharer()
    
    st.title("📍 Location Distance Calculator")
    st.markdown("Upload your locations CSV file to find users sorted by distance from a reference point.")
    
    # Create two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload CSV File")
        uploaded_file = st.file_uploader(
            "Choose your locations.csv file", 
            type="csv",
            help="Upload the CSV file downloaded from your location tracker"
        )
    
    with col2:
        st.subheader("🎯 Set Reference Point")
        st.info("Enter the coordinates you want to measure distances from")
        
        ref_lat = st.number_input(
            "Reference Latitude", 
            value=40.7128,
            format="%.6f",
            help="e.g., 40.7128 for New York"
        )
        
        ref_lon = st.number_input(
            "Reference Longitude", 
            value=-74.0060,
            format="%.6f",
            help="e.g., -74.0060 for New York"
        )
    
    st.markdown("---")
    
    if uploaded_file is not None:
        # Process the CSV file
        with st.spinner("Processing locations and calculating distances..."):
            df = process_locations_csv(uploaded_file, ref_lat, ref_lon)
        
        if df is not None and not df.empty:
            st.success(f"✅ Processed {len(df)} locations successfully!")
            
            # Display summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Locations", len(df))
            
            with col2:
                st.metric("Closest Distance", f"{df['Distance_km'].min():.2f} km")
            
            with col3:
                st.metric("Farthest Distance", f"{df['Distance_km'].max():.2f} km")
            
            with col4:
                st.metric("Average Distance", f"{df['Distance_km'].mean():.2f} km")
            
            # Display the sorted data with distance order
            st.subheader("📊 Users Sorted by Distance (Ordered from 0)")
            
            # Create a more user-friendly display
            display_df = df.copy()
            display_df['Distance'] = display_df['Distance_km'].apply(lambda x: f"{x:.2f} km")
            
            # Select columns to display - INCLUDING Distance_Order
            columns_to_show = ['Distance_Order', 'ID', 'Device', 'Latitude', 'Longitude', 'Distance', 'Timestamp']
            available_columns = [col for col in columns_to_show if col in display_df.columns]
            
            # Reorder columns to show Distance_Order first
            if 'Distance_Order' in available_columns:
                available_columns.remove('Distance_Order')
                available_columns = ['Distance_Order'] + available_columns
            
            st.dataframe(
                display_df[available_columns],
                use_container_width=True,
                height=400
            )
            
            # NEW FEATURE: Find users close to last registered user
            st.subheader("👥 Users Near Last Registered User")
            
            # Let user set the distance threshold
            max_distance = st.slider(
                "Maximum distance to consider as 'nearby' (km)",
                min_value=1,
                max_value=50,
                value=10,
                help="Set the maximum distance in kilometers to find users near the last registered user"
            )
            
            last_user, nearby_users, last_coords = find_nearby_users(df, max_distance)
            
            if last_user is not None:
                # Add distance order for nearby users
                if not nearby_users.empty:
                    nearby_users = nearby_users.sort_values('Distance_From_Last_User_km')
                    nearby_users['Nearby_Order'] = range(len(nearby_users))
                
                st.info(f"**Last Registered User:** {last_user.get('ID', 'Unknown')} at coordinates ({last_coords[0]:.6f}, {last_coords[1]:.6f})")
                
                if not nearby_users.empty:
                    st.success(f"Found {len(nearby_users)} user(s) within {max_distance} km of the last registered user:")
                    
                    # Display nearby users with order
                    nearby_display = nearby_users.copy()
                    nearby_display['Distance_From_Last_User'] = nearby_display['Distance_From_Last_User_km'].apply(lambda x: f"{x:.2f} km")
                    
                    nearby_columns = ['Nearby_Order', 'ID', 'Device', 'Latitude', 'Longitude', 'Distance_From_Last_User', 'Timestamp']
                    available_nearby_columns = [col for col in nearby_columns if col in nearby_display.columns]
                    
                    # Reorder to show Nearby_Order first
                    if 'Nearby_Order' in available_nearby_columns:
                        available_nearby_columns.remove('Nearby_Order')
                        available_nearby_columns = ['Nearby_Order'] + available_nearby_columns
                    
                    st.dataframe(
                        nearby_display[available_nearby_columns],
                        use_container_width=True
                    )
                    
                    # Show nearby users on map
                    st.subheader("🗺️ Nearby Users Map")
                    if 'Latitude' in nearby_display.columns and 'Longitude' in nearby_display.columns:
                        # Combine last user and nearby users for the map
                        map_data = pd.concat([
                            pd.DataFrame([{
                                'lat': last_coords[0],
                                'lon': last_coords[1],
                                'Type': 'Last User'
                            }]),
                            prepare_for_mapping(nearby_users)[['lat', 'lon']].assign(Type='Nearby User')
                        ], ignore_index=True)
                        
                        st.map(map_data)
                else:
                    st.warning(f"No other users found within {max_distance} km of the last registered user.")
            
            # Show on map - FIXED: Use prepared dataframe with correct column names
            st.subheader("🗺️ All Locations Map")
            map_df = prepare_for_mapping(df)
            st.map(map_df[['lat', 'lon']])
            
            # Download processed data
            st.subheader("📥 Download Processed Data")
            
            # Convert processed dataframe to CSV
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="Download Sorted Locations CSV",
                data=csv,
                file_name="sorted_locations_by_distance.csv",
                mime="text/csv",
                help="Download the locations sorted by distance"
            )
            
            # Raw data expander
            with st.expander("📋 View Raw Data"):
                st.dataframe(df, use_container_width=True)
                
        else:
            st.error("No valid location data found in the CSV file.")
    
    else:
        # Show instructions when no file is uploaded
        st.info("👆 Please upload a CSV file to get started")
        
        with st.expander("📖 How to use this app"):
            st.markdown("""
            1. **Download your locations CSV** from your location tracker app
            2. **Upload the CSV file** using the file uploader above
            3. **Set reference coordinates** - the point from which to measure distances
            4. **View results** - users will be sorted by distance from your reference point (starting from 0)
            5. **Find nearby users** - discover which users are close to the last registered user
            
            **Expected CSV format:**
            - Columns: ID, Device, Latitude, Longitude, Accuracy, Timestamp, UserAgent, CreatedAt
            - The app will automatically clean and process the data
            
            **Distance Order:** Locations are numbered from 0 (closest) to N (farthest) from your reference point
            """)

# Run both main app and SMS sharer
if __name__ == "__main__":
    main()
