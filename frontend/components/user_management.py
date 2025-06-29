import streamlit as st
import requests

API_URL = "http://localhost:8000/api"

def user_management_page():
    st.title("👥 User Management")
    st.info("Admins can create all roles. Pro users can create staff/employees (max 5 users). New users inherit your plan.")

    token = st.session_state.get("token")
    user_info = st.session_state.get("user")
    user_role = user_info.get("role", "employee") if user_info else "employee"
    plan_id = user_info.get("plan_id", "basic") if user_info else "basic"

    headers = {"Authorization": f"Bearer {token}"}
    
    # Fetch users
    users = []
    try:
        resp = requests.get(f"{API_URL}/users", headers=headers)
        if resp.status_code == 200:
            users = resp.json()
        else:
            st.error(f"Failed to fetch users. Status: {resp.status_code}")
            if resp.status_code == 403:
                st.error("Access denied. You may not have permission to view users.")
            elif resp.status_code == 401:
                st.error("Authentication required. Please log in again.")
    except Exception as e:
        st.error(f"Error fetching users: {e}")

    # Show user count and plan limit for Pro
    if plan_id == "pro":
        st.warning(f"Pro Plan: {len(users)}/5 users (max 5)")
        can_add = len(users) < 5
    else:
        can_add = True

    st.subheader("Current Users")
    
    # Display users with edit/delete buttons
    for i, u in enumerate(users):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"**{u['username']}** ({u['role']}) | {u.get('email', '')}")
        with col2:
            if st.button(f"Edit", key=f"edit_{i}"):
                st.session_state.edit_user = u
        with col3:
            if st.button(f"Delete", key=f"delete_{i}"):
                st.session_state.delete_user = u

    # Edit User Modal
    if st.session_state.get("edit_user"):
        user_to_edit = st.session_state.edit_user
        with st.form("edit_user_form", clear_on_submit=True):
            st.subheader(f"Edit User: {user_to_edit['username']}")
            edit_username = st.text_input("Username", value=user_to_edit['username'])
            edit_email = st.text_input("Email", value=user_to_edit.get('email', ''))
            edit_password = st.text_input("New Password (leave blank to keep current)", type="password")
            
            # Role selection based on current user permissions
            if user_role == "admin":
                edit_role = st.selectbox("Role", ["admin", "staff", "employee"], 
                                       index=["admin", "staff", "employee"].index(user_to_edit['role']))
            elif user_role == "staff":
                edit_role = st.selectbox("Role", ["employee"], index=0)
            else:
                edit_role = "employee"
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Update User"):
                    payload = {
                        "username": edit_username,
                        "email": edit_email,
                        "password": edit_password if edit_password else "",
                        "role": edit_role
                    }
                    try:
                        resp = requests.put(f"{API_URL}/users/{user_to_edit.get('id')}", 
                                          json=payload, headers=headers)
                        if resp.status_code == 200:
                            st.success("User updated successfully!")
                            st.session_state.edit_user = None
                            st.rerun()
                        else:
                            try:
                                st.error(resp.json().get("detail", "Failed to update user."))
                            except:
                                st.error("Failed to update user.")
                    except Exception as e:
                        st.error(f"Error: {e}")
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.edit_user = None
                    st.rerun()

    # Delete User Confirmation
    if st.session_state.get("delete_user"):
        user_to_delete = st.session_state.delete_user
        st.warning(f"Are you sure you want to delete user '{user_to_delete['username']}'?")
        st.info("This will preserve all incidents submitted by this user.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Delete"):
                try:
                    resp = requests.delete(f"{API_URL}/users/{user_to_delete.get('id')}", 
                                         headers=headers)
                    if resp.status_code == 200:
                        st.success("User deleted successfully!")
                        st.session_state.delete_user = None
                        st.rerun()
                    else:
                        try:
                            st.error(resp.json().get("detail", "Failed to delete user."))
                        except:
                            st.error("Failed to delete user.")
                except Exception as e:
                    st.error(f"Error: {e}")
        with col2:
            if st.button("Cancel"):
                st.session_state.delete_user = None
                st.rerun()

    # Add User Form
    if can_add:
        with st.form("add_user_form", clear_on_submit=True):
            st.subheader("Add New User")
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            
            # Role selection
            if user_role == "admin":
                new_role = st.selectbox("Role", ["admin", "staff", "employee"])
            elif user_role == "staff":
                new_role = st.selectbox("Role", ["employee"])
            else:
                new_role = "employee"
            
            # Store assignment
            store_id = None
            if user_role == "admin":
                # Admin can assign to any store or no store
                store_options = ["No Store"] + [f"Store #{i:03d}" for i in range(1, 101)]  # Simple store options
                selected_store = st.selectbox("Store Assignment", store_options)
                if selected_store != "No Store":
                    store_id = int(selected_store.split("#")[1])
            elif user_role == "staff":
                # Staff can only assign to their own store
                if user_info.get('store'):
                    store_info = user_info['store']
                    st.info(f"Store Assignment: {store_info['store_number']} - {store_info['location']}")
                    store_id = store_info['id']
                else:
                    st.error("You must be assigned to a store to create users.")
                    st.stop()
            
            submit_user = st.form_submit_button("Create User")
            if submit_user:
                if len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    payload = {
                        "username": new_username,
                        "email": new_email,
                        "password": new_password,
                        "role": new_role,
                        "store_id": store_id
                    }
                    try:
                        resp = requests.post(f"{API_URL}/users/create", json=payload, headers=headers)
                        if resp.status_code == 200:
                            st.success("User created successfully!")
                            st.rerun()
                        else:
                            try:
                                st.error(resp.json().get("detail", "Failed to create user."))
                            except:
                                st.error("Failed to create user.")
                    except Exception as e:
                        st.error(f"Error: {e}")
    else:
        st.info("Pro plan user limit reached. Upgrade to Enterprise for unlimited users.") 