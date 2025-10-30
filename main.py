import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="BOM & Life Cycle Merger", layout="wide")
st.title("BOM & Life Cycle Data Merger")

# Create columns for layout
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📤 BOM File")
    bom_file = st.file_uploader("Upload BOM Excel file (.xlsx or .xls)", type=['xlsx', 'xls'], key="bom")

with col2:
    st.subheader("📤 Life Cycle File")
    life_cycle_file = st.file_uploader("Upload Life Cycle Excel file (.xlsx or .xls)", type=['xlsx', 'xls'],
                                       key="life_cycle")

with col3:
    st.subheader("🏷️ MTS Codes")
    mts_input = st.text_area(
        "Enter MTS codes:",
        height=150,
        placeholder="MTS001\nMTS002\nPLACEHOLDER FOR DEVICE123\n\nOr comma-separated: MTS001,MTS002,DEVICE123"
    )

# Submit button
st.markdown("---")
submit_button = st.button("🔄 Process Data", type="primary", use_container_width=True)

# Process when submit button is clicked
if submit_button:
    if not bom_file or not life_cycle_file or not mts_input:
        st.error("❌ Please upload both files and enter MTS codes")
    else:
        try:
            # Parse MTS list
            if ',' in mts_input:
                mts_list = [code.strip() for code in mts_input.split(',')]
            else:
                mts_list = [code.strip() for code in mts_input.split('\n')]

            mts_list = [code for code in mts_list if code]

            if not mts_list:
                st.error("❌ Please enter at least one MTS code")
            else:
                # Read files
                with st.spinner("Reading files..."):
                    bom_df = pd.read_excel(bom_file)
                    life_cycle_df = pd.read_excel(life_cycle_file)

                st.success("✓ Files loaded successfully")
                st.info(
                    f"📌 Filtering by {len(mts_list)} MTS codes: {', '.join(mts_list[:5])}{'...' if len(mts_list) > 5 else ''}")

                # Filter BOM by MTS codes
                bom_filtered = bom_df[bom_df['MTS'].isin(mts_list)].copy()

                if bom_filtered.empty:
                    st.warning("⚠️ No rows found matching the provided MTS codes")
                else:
                    # Merge with Life Cycle data
                    output_df = bom_filtered.merge(
                        life_cycle_df[['PN', 'Limit']],
                        on='PN',
                        how='left'
                    )

                    # Create output table with specified columns
                    output_df_final = pd.DataFrame({
                        "SW /HCA": "",
                        "Product Lines": output_df['ProductLines'],
                        "StationTypes": output_df['StationTypes'],
                        "MTS": output_df['MTS'],
                        "PN (SFG\\SA)": output_df['PN (SFG\\SA)'],
                        "PN": output_df['PN'],
                        "Alternative PN": output_df['Alternative PN'],
                        "Description": output_df['Description'],
                        "Group": output_df['Group'],
                        "BOM Quantity": output_df['Quantity'],
                        "Life Cycle Limit": output_df['Limit'],
                        "ProductName": output_df['ProductName'],
                        "Vendor": output_df['Vendor'],
                        "DefaultMinQuantity": output_df['DefaultMinQuantity'],
                        "Related to ACC-KIT": output_df['Related to ACC-KIT'],
                        "Relation": output_df['Relation']
                    })

                    # Display results
                    st.subheader("📊 Preview")
                    st.dataframe(output_df_final, use_container_width=True)

                    st.success(f"✓ Successfully processed {len(output_df_final)} rows")

                    # Download buttons
                    st.markdown("---")
                    col_csv, col_excel = st.columns(2)

                    with col_csv:
                        csv_buffer = io.StringIO()
                        output_df_final.to_csv(csv_buffer, index=False)
                        csv_data = csv_buffer.getvalue()

                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv_data,
                            file_name="output.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

                    with col_excel:
                        excel_buffer = io.BytesIO()
                        output_df_final.to_excel(excel_buffer, index=False, sheet_name="Output")
                        excel_buffer.seek(0)

                        st.download_button(
                            label="📥 Download as Excel",
                            data=excel_buffer.getvalue(),
                            file_name="output.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )

        except KeyError as e:
            st.error(f"❌ Column not found: {e}. Please check your files have the expected columns.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")