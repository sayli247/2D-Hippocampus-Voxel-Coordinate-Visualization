#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 15:08:01 2024

@author: saylipatil
"""

# Final Program 

import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events
import datetime
from shift_on_grid import shift_on_grid

finished_gridding = False

# Function to load .xyz file
def load_xyz(file):
    data = np.loadtxt(file)
    return data

# Function to save data to a .xyz file
def save_xyz(data, filename):
    np.savetxt(filename, data, fmt='%.6f')

# Initialize or retrieve the list of additional points from session state
if 'additional_points' not in st.session_state:
    st.session_state.additional_points = []

# Initialize finished_gridding to keep track of when gridding is done in session state
if "finished_gridding" not in st.session_state:
    st.session_state.finished_gridding = False
if "gridded_np_data" not in st.session_state:
    st.session_state.gridded_np_data = None

# Streamlit UI
st.title("2D Slice Viewer")

# File uploader
uploaded_file = st.file_uploader("Choose a .xyz file", type="xyz")

if uploaded_file is not None:
    # Load the data
    data = load_xyz(uploaded_file)

    # Extract unique z-values for the dropdown
    unique_z_values = np.unique(data[:, 2])
    selected_z = st.selectbox("Select z-value", unique_z_values)

    # Get the index of the selected z-value
    selected_index = np.where(unique_z_values == selected_z)[0][0]

    # Determine the z-values for the before and after slices
    if selected_index > 0:
        before_z = unique_z_values[selected_index - 1]
    else:
        before_z = None

    if selected_index < len(unique_z_values) - 1:
        after_z = unique_z_values[selected_index + 1]
    else:
        after_z = None

    # Filter data for the selected z-value
    slice_data = data[data[:, 2] == selected_z]

    # Filter data for before and after slices
    if before_z is not None:
        before_slice_data = data[data[:, 2] == before_z]
    
    if after_z is not None:
        after_slice_data = data[data[:, 2] == after_z]
    
    # Plotting
    fig = go.Figure()

    # Add scatter points for the selected z-value slice with larger white dots
    fig.add_trace(go.Scatter(x=slice_data[:, 0], y=slice_data[:, 1], mode='markers', 
                             name=f'Slice at z = {selected_z}', marker=dict(color='blue', size=10)))
    
    # Add scatter points for the before slice with smaller blue dots
    if before_z is not None:
        fig.add_trace(go.Scatter(x=before_slice_data[:, 0], y=before_slice_data[:, 1], mode='markers', 
                                 name=f'Slice at z = {before_z}', marker=dict(color='red', size=5)))

    # Add scatter points for the after slice with smaller red dots
    if after_z is not None:
        fig.add_trace(go.Scatter(x=after_slice_data[:, 0], y=after_slice_data[:, 1], mode='markers', 
                                 name=f'Slice at z = {after_z}', marker=dict(color='white', size=3)))

    fig.update_layout(title='Slice comparison', template='plotly')
    st.plotly_chart(fig, use_container_width=True)
            
    # Plot the 2D slice
    fig = px.scatter(x=slice_data[:, 0], y=slice_data[:, 1], title=f"2D Slice at z = {selected_z}", template="plotly")
    st.plotly_chart(fig, use_container_width=True)
    
    # Radio buttons for choosing mode
    mode = st.radio("Choose action:", ("","Add points", "Delete points", "Grid points"), index = 0)
    
    if mode == "Add points":
        # Define the dimensions of the grid with padding
        padding = 100  # Adjust this value to increase/decrease the padding
        x_min, x_max = slice_data[:, 0].min() - padding, slice_data[:, 0].max() + padding
        y_min, y_max = slice_data[:, 1].min() - padding, slice_data[:, 1].max() + padding
        
        # Generate a dense grid of points with resolution 1x1
        x_values = np.arange(x_min, x_max + 1)
        y_values = np.arange(y_min, y_max + 1)
        x_grid, y_grid = np.meshgrid(x_values, y_values)
        
        # Create a heatmap with black color (no real z-values used)
        # Heatmap was used instead of scatter plot due to slow loading issue
        heatmap = go.Heatmap(
            x=x_grid.flatten(),
            y=y_grid.flatten(),
            z=np.zeros_like(x_grid.flatten()),  # No actual z-values are needed
            colorscale=[[0, 'black'], [1, 'black']],
            showscale=False,
            hoverinfo='none'
        )
        
        # Create a scatter plot with white points for the selected z-slice
        scatter = go.Scatter(
            x=slice_data[:, 0],
            y=slice_data[:, 1],
            mode='markers',
            marker=dict(color='white', size=5),
            hoverinfo='none'
        )
        
        # Define the layout
        layout = go.Layout(
            title=f"2D Slice at z = {selected_z}",
            xaxis=dict(title='x', range=[x_min, x_max]),
            yaxis=dict(title='y', range=[y_min, y_max]),
            plot_bgcolor='black',
            paper_bgcolor='black'
        )
        
        # Create the figure
        fig = go.Figure(data=[heatmap, scatter], layout=layout)
        
        # Display the Plotly figure and capture click events
        selected_points = plotly_events(fig, click_event=True)
        
        # If there are selected points
        if selected_points:
            # Extract the middle point from the click events
            middle_point = selected_points[1] if len(selected_points) > 1 else selected_points[0]

            x_click = middle_point['x']
            y_click = middle_point['y']
            
            # Add the clicked point to the list of points in session state
            st.session_state.additional_points.append((x_click, y_click, selected_z))
            
            # Convert additional_points to NumPy array for easy manipulation
            additional_points_np = np.array(st.session_state.additional_points)
            
            # Ensure the additional_points_np has the correct shape
            if additional_points_np.shape[1] != 3:
                st.error("Additional points should have exactly three columns (x, y, z).")
            else:
                # Combine the original slice data with additional points
                slice_data_reduced = slice_data[:, :3]  # Ensure it only has x, y, z
                combined_data = np.vstack([slice_data_reduced, additional_points_np])
                
                # Update the scatter plot with all additional white points
                updated_scatter = go.Scatter(
                    x=combined_data[:, 0],
                    y=combined_data[:, 1],
                    mode='markers',
                    marker=dict(color='white', size=5),
                    text=[f'x: {x:.2f}<br>y: {y:.2f}<br>z: {z:.2f}' for x, y, z in combined_data],
                    hoverinfo='text',
                    name=f'Slice at z = {selected_z}'
                )
                
                # Define layout for the new figure without heatmap
                new_layout = go.Layout(
                    title=f"Updated Slice at z = {selected_z} (with clicked points)",
                    xaxis=dict(title='x', range=[x_min, x_max]),
                    yaxis=dict(title='y', range=[y_min, y_max]),
                    plot_bgcolor='black',
                    paper_bgcolor='black'
                )
                
                # Create the new figure with updated scatter plot
                new_fig = go.Figure(data=[updated_scatter], layout=new_layout)
                
                # Display the updated plot with white points on a black background
                st.plotly_chart(new_fig)
                
                # Display the clicked point
                st.write(f"You clicked on the following point: x = {x_click}, y = {y_click}")
                
                # Save button to trigger the saving process
                if st.button("Save modified data"):
                    # Keep only the first 3 columns from the original dataset
                    modified_data = data[:, :3]
                    
                    # Convert additional_points to NumPy array for easy manipulation
                    additional_points_np = np.array(st.session_state.additional_points)
                    
                    # Ensure the additional_points_np has the correct shape
                    if additional_points_np.shape[1] != 3:
                        st.error("Additional points should have exactly three columns (x, y, z).")
                    else:
                        # Remove the selected slice data from the original dataset
                        modified_data = modified_data[modified_data[:, 2] != selected_z]
                        
                        # Combine the modified slice data with the modified original dataset
                        combined_data = np.vstack([modified_data, additional_points_np])
                        
                        # Generate a timestamp for the filename
                        timestamp = datetime.datetime.now().strftime("%Y.%m.%d - %H-%M-%S")
                        
                        # Provide a filename for saving
                        filename = f"{timestamp}.xyz"
                        
                        # Save the combined data to a .xyz file
                        save_xyz(combined_data, filename)
                        
                        st.write(f"Updated .xyz file saved as {filename}")
                    
                    
    elif mode == "Delete points":
        # Display the Plotly figure and capture click events
        # selected_points = plotly_events(fig, click_event=True)
        selected_points = plotly_events(fig, select_event=True)


        # Use session state to keep track of removed points
        if 'removed_points' not in st.session_state:
            st.session_state.removed_points = []

        if selected_points:
            # Get the first selected point
            # point_to_remove = selected_points[0]
            points_to_remove = selected_points

            # Print the coordinates of the selected point
            st.write("The selected points are: ")
            for elem in selected_points:
                st.write(f"x: {elem['x']}, y: {elem['y']}")

            # Button to remove the point
            if st.button("Remove selected points"):
                # Parse the selected point's coordinates

                for elem in selected_points:
                    point_x = elem['x']
                    point_y = elem['y']
                    
                    # Add the point to the removed points list
                    st.session_state.removed_points.append((point_x, point_y))

                # Filter out removed points from slice_data
                mask = np.array([(x, y) not in st.session_state.removed_points for x, y in zip(slice_data[:, 0], slice_data[:, 1])])
                slice_data = slice_data[mask]

                # Re-plot the updated slice data
                fig = px.scatter(x=slice_data[:, 0], y=slice_data[:, 1], title=f"Updated 2D Slice at z = {selected_z}", template="plotly")
                st.plotly_chart(fig)

        # Display the "Save modified data" button only if there are removed points
        if st.session_state.removed_points:
            if st.button("Save modified data"):
                # Filter out removed points from the original data
                mask = np.array([(x, y, z) not in st.session_state.removed_points for x, y, z in zip(data[:, 0], data[:, 1], data[:, 2])])
                modified_data = data[mask]
                
                modified_data = modified_data[:, :3]
                
                # Generate a timestamp for the filename
                timestamp = datetime.datetime.now().strftime("%Y.%m.%d - %H-%M-%S")
                
                # Provide a filename for saving
                filename = f"{timestamp}.xyz"
                
                # Save the combined data to a .xyz file
                save_xyz(modified_data, filename)
                
                st.write(f"Updated .xyz file saved as {filename}")
                
    elif mode == "Grid points": 
        # Start gridding when radio button pressed
        import time
        st.write("Points are gridded to the nearest bin that is a multiple of 16")
        time.sleep(1)
        if not st.session_state.finished_gridding:
            print("inside with loop")
            with st.spinner(text="Gridding... this will take a few minutes"):
                # Run shift_on_grid function to grid the points and put into numpy array
                gridded_data = shift_on_grid(data) # Grid the data (long runtime)
                st.session_state.gridded_np_data = np.asarray(gridded_data, dtype=np.float64) # Convert to numpy array
                st.session_state.finished_gridding = True

        gridded_np_data = st.session_state.gridded_np_data
        # Grab updated slice data
        gridded_slice_data = gridded_np_data[gridded_np_data[:, 2] == selected_z]
        # Re-plot the updated slice data
        fig = px.scatter(x=gridded_slice_data[:, 0], y=gridded_slice_data[:, 1], title=f"Updated 2D Slice at z = {selected_z}", template="plotly")
        st.plotly_chart(fig)

        # Load in save button for the data
        if st.session_state.finished_gridding:
            save_file = st.button("Save shifted data")
            if save_file:
                print("pressed save file")
                save_xyz(gridded_np_data, "gridded_data.xyz")
                st.success("Shifted data saved to 'gridded_data.xyz'")

    
    
    else:
        st.write("No action selected")

