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
        
        return df
        
    except Exception as e:
        st.error(f"Error processing CSV file: {str(e)}")
        return None

# Main Streamlit app
def main():
    st.set_page_config(
        page_title="Location Distance Calculator",
        page_icon="📍",
        layout="wide"
    )
    
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
            
            # Display the sorted data
            st.subheader("📊 Users Sorted by Distance")
            
            # Create a more user-friendly display
            display_df = df.copy()
            display_df['Distance'] = display_df['Distance_km'].apply(lambda x: f"{x:.2f} km")
            
            # Select columns to display
            columns_to_show = ['ID', 'Device', 'Latitude', 'Longitude', 'Distance', 'Timestamp']
            available_columns = [col for col in columns_to_show if col in display_df.columns]
            
            st.dataframe(
                display_df[available_columns],
                use_container_width=True,
                height=400
            )
            
            # Show on map
            st.subheader("🗺️ Locations Map")
            st.map(df[['Latitude', 'Longitude']])
            
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
            4. **View results** - users will be sorted by distance from your reference point
            
            **Expected CSV format:**
            - Columns: ID, Device, Latitude, Longitude, Accuracy, Timestamp, UserAgent, CreatedAt
            - The app will automatically clean and process the data
            """)

# SMS sharing functionality (your original feature)
def sms_sharer():
    st.markdown("---")
    st.subheader("📲 Share App Link")
    
    app_url = "https://your-location-tracker.onrender.com/"  # Update with your actual URL
    
    st.write("**App Link:**")
    st.code(app_url)
    
    st.subheader("Quick Share:")
    phone = st.text_input("Enter phone number:", key="phone")
    
    if phone:
        message = f"Check out this location sharing app: {app_url}"
        sms_url = f"sms:{phone}?body={message}"
        
        st.markdown(
            f'<a href="{sms_url}" target="_blank">'
            '<button style="background-color:green;color:white;padding:10px;border:none;border-radius:5px;">'
            'Send SMS</button></a>', 
            unsafe_allow_html=True
        )
    
    st.info("💡 The SMS button will open your phone's messaging app with the link pre-filled.")

# Run both main app and SMS sharer
if __name__ == "__main__":
    main()
    sms_sharer()
