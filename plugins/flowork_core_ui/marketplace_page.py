#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\plugins\flowork_core_ui\marketplace_page.py
# JUMLAH BARIS : 496
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
from flowork_kernel.api_client import ApiClient
import os
import threading
from flowork_kernel.utils.performance_logger import log_performance
import json
import webbrowser
import requests
import tempfile
from .upload_dialog import UploadDialog
class MarketplacePage(ttk.Frame):
    def __init__(self, parent_notebook, kernel_instance):
        super().__init__(parent_notebook)
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient()
        self.local_component_trees = {}
        self.community_component_trees = {}
        self.local_cache = {}
        self.community_cache = {}
        self.main_notebook = None
        self.ui_ready = False
        self._build_ui()
        self._fetch_all_data_and_refresh()
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            subscriber_id = f"marketplace_page_{id(self)}"
            event_bus.subscribe("COMPONENT_LIST_CHANGED", subscriber_id, self.refresh_content)
    def _build_ui(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill='both', expand=True)
        self.ads_frame = ttk.LabelFrame(main_frame, text="Community Highlights", padding=10, width=350)
        self.ads_frame.pack(side='right', fill='y', padx=(10, 0))
        self.ads_frame.pack_propagate(False)
        left_pane = ttk.Frame(main_frame)
        left_pane.pack(side='left', fill='both', expand=True)
        action_frame = ttk.Frame(left_pane)
        action_frame.pack(fill='x', pady=(0, 10))
        self.install_button = ttk.Button(action_frame, text=self.loc.get('marketplace_install_btn', fallback="Install from Zip..."), command=self._install_component, bootstyle="success")
        self.install_button.pack(side='left', padx=(0, 10))
        self.upload_button = ttk.Button(action_frame, text=self.loc.get('marketplace_upload_btn', fallback="Upload to Community..."), command=self._upload_selected_component, bootstyle="info")
        self.upload_button.pack(side='left', padx=(0,10))
        self.toggle_button = ttk.Button(action_frame, text=self.loc.get('marketplace_disable_btn', fallback="Disable Selected"), command=self._toggle_selected_component, bootstyle="warning")
        self.toggle_button.pack(side='left', padx=(0, 10))
        self.uninstall_button = ttk.Button(action_frame, text=self.loc.get('marketplace_uninstall_btn', fallback="Uninstall Selected"), command=self._uninstall_selected_component, bootstyle="danger")
        self.uninstall_button.pack(side='left')
        search_bar_frame = ttk.Frame(left_pane)
        search_bar_frame.pack(fill='x', pady=(0, 10))
        self.search_var = ttk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        search_entry = ttk.Entry(search_bar_frame, textvariable=self.search_var)
        search_entry.pack(fill='x', expand=True)
        search_entry.insert(0, self.loc.get('marketplace_search_placeholder', fallback="Search by Name, ID, or Description..."))
        self.main_notebook = ttk.Notebook(left_pane)
        self.main_notebook.pack(fill='both', expand=True)
        self.main_notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)
        local_tab = ttk.Frame(self.main_notebook)
        community_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(local_tab, text=self.loc.get('marketplace_tab_local', fallback="Locally Installed"))
        self.main_notebook.add(community_tab, text=self.loc.get('marketplace_tab_community', fallback="Community"))
        self._create_component_notebook(local_tab, self.local_component_trees)
        self._create_component_notebook(community_tab, self.community_component_trees)
        self.ui_ready = True
    def refresh_content(self, event_data=None):
        self.kernel.write_to_log("MarketplacePage received a signal to refresh its content.", "INFO")
        self._fetch_all_data_and_refresh()
    def _fetch_all_data_and_refresh(self):
        threading.Thread(target=self._fetch_all_data_worker, daemon=True).start()
    def _create_component_notebook(self, parent_tab, tree_dict):
        notebook = ttk.Notebook(parent_tab)
        notebook.pack(fill='both', expand=True)
        component_types = {
            "modules": self.loc.get('marketplace_tab_modules', fallback="Modules"),
            "plugins": self.loc.get('marketplace_tab_plugins', fallback="Plugins"),
            "widgets": self.loc.get('marketplace_tab_widgets', fallback="Widgets"),
            "presets": self.loc.get('marketplace_tab_presets', fallback="Presets"),
            "triggers": "Triggers",
            "ai_providers": "AI Providers",
            "ai_models": "AI Models"
        }
        is_monet_active = self.kernel.is_monetization_active() # (PENAMBAHAN) Cek status monetisasi sekali saja
        for comp_type, tab_title in component_types.items():
            tab = ttk.Frame(notebook, padding=5)
            notebook.add(tab, text=tab_title)
            columns = ["name", "description"]
            if is_monet_active:
                columns.append("tier")
            if comp_type == 'ai_models':
                columns.append("downloads")
            else:
                columns.append("version")
            columns.append("status")
            tree = ttk.Treeview(tab, columns=tuple(columns), show="headings")
            tree.heading("name", text=self.loc.get('marketplace_col_name', fallback="Addon Name"))
            tree.column("name", width=250)
            tree.heading("description", text=self.loc.get('marketplace_col_desc', fallback="Description"))
            tree.column("description", width=400)
            if is_monet_active:
                tree.heading("tier", text=self.loc.get('marketplace_col_tier', fallback="Tier"))
                tree.column("tier", width=80, anchor='center')
            if comp_type == 'ai_models':
                tree.heading("downloads", text=self.loc.get('marketplace_col_downloads', fallback="Downloads"))
                tree.column("downloads", width=80, anchor='center')
            else:
                tree.heading("version", text=self.loc.get('marketplace_col_version', fallback="Version"))
                tree.column("version", width=80, anchor='center')
            tree.heading("status", text=self.loc.get('marketplace_col_status', fallback="Status"))
            tree.column("status", width=100, anchor='center')
            tree.pack(fill='both', expand=True)
            tree.bind('<<TreeviewSelect>>', self._update_button_state)
            tree_dict[comp_type] = tree
    def _populate_ads_panel(self, success, ads_data):
        if not self.winfo_exists() or not self.ads_frame.winfo_exists():
            return
        for widget in self.ads_frame.winfo_children():
            widget.destroy()
        if not success or not ads_data:
            ttk.Label(self.ads_frame, text="Cannot load highlights at the moment.").pack()
            return
        styles = ["primary", "info", "success", "warning", "danger", "secondary"]
        for i, ad in enumerate(ads_data):
            style = styles[i % len(styles)]
            ad_card = ttk.LabelFrame(self.ads_frame, text=ad.get("title", "Ad"), padding=10, bootstyle=style)
            ad_card.pack(fill="x", pady=5)
            ttk.Label(ad_card, text=ad.get("text", ""), wraplength=280).pack(anchor='w', pady=(0, 10))
            if "target_url" in ad and "button_text" in ad:
                ttk.Button(
                    ad_card,
                    text=ad.get("button_text"),
                    bootstyle=f"{style}-outline",
                    command=lambda url=ad.get("target_url"): webbrowser.open(url)
                ).pack(anchor='e')
    def _get_current_tab_info(self):
        try:
            if not self.main_notebook or not self.main_notebook.winfo_exists():
                return None, None, True
            active_main_tab_text = self.main_notebook.tab(self.main_notebook.select(), "text")
            if self.loc.get('marketplace_tab_local', fallback="Locally Installed") in active_main_tab_text:
                if not self.main_notebook.nametowidget(self.main_notebook.select()).winfo_exists():
                    return None, None, True
                notebook = self.main_notebook.nametowidget(self.main_notebook.select()).winfo_children()[0]
                tree_dict = self.local_component_trees
                is_local = True
            else:
                if not self.main_notebook.nametowidget(self.main_notebook.select()).winfo_exists():
                    return None, None, False
                notebook = self.main_notebook.nametowidget(self.main_notebook.select()).winfo_children()[0]
                tree_dict = self.community_component_trees
                is_local = False
            if not notebook.winfo_exists():
                return None, None, is_local
            tab_text = notebook.tab(notebook.select(), "text").strip()
            tab_map = {
                self.loc.get('marketplace_tab_modules', fallback="Modules"): 'modules',
                self.loc.get('marketplace_tab_plugins', fallback="Plugins"): 'plugins',
                self.loc.get('marketplace_tab_widgets', fallback="Widgets"): 'widgets',
                self.loc.get('marketplace_tab_presets', fallback="Presets"): 'presets',
                "Triggers": 'triggers',
                "AI Providers": 'ai_providers',
                "AI Models": 'ai_models'
            }
            comp_type = tab_map.get(tab_text, 'modules')
            return comp_type, tree_dict.get(comp_type), is_local
        except Exception:
            return 'modules', self.local_component_trees.get('modules'), True
    def _fetch_all_data_worker(self):
        threads = []
        def fetch_component_data(comp_type):
            success_local, local_data = self.api_client.get_components(comp_type)
            self.local_cache[comp_type] = local_data if success_local else []
            if not success_local:
                self.kernel.write_to_log(f"API Error fetching local {comp_type}: {local_data}", "ERROR")
            success_remote, remote_data = self.api_client.get_marketplace_index(comp_type)
            self.community_cache[comp_type] = remote_data if success_remote else []
            if not success_remote:
                self.kernel.write_to_log(f"API Error fetching remote {comp_type}: {remote_data}", "WARN")
        for comp_type in self.local_component_trees.keys():
            thread = threading.Thread(target=fetch_component_data, args=(comp_type,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        success_ads, ads_data = self.api_client.get_marketplace_ads()
        self.after(0, self._refresh_all_lists)
        self.after(0, self._populate_ads_panel, success_ads, ads_data)
    def _refresh_all_lists(self):
        for comp_type in self.local_component_trees.keys():
            self._refresh_list(comp_type, self.local_component_trees.get(comp_type), self.local_cache, is_local_tab=True)
        for comp_type in self.community_component_trees.keys():
            self._refresh_list(comp_type, self.community_component_trees.get(comp_type), self.community_cache, is_local_tab=False)
        self._update_button_state()
    def _refresh_list(self, component_type, tree, data_cache, is_local_tab):
        if not tree or not tree.winfo_exists():
            return
        for item in tree.get_children():
            tree.delete(item)
        search_query = self.search_var.get().lower()
        if search_query == self.loc.get('marketplace_search_placeholder', fallback="Search by Name, ID, or Description...").lower():
            search_query = ""
        search_keywords = search_query.split()
        data = data_cache.get(component_type, [])
        all_local_ids = set()
        for c_type in self.local_cache.keys():
            for item in self.local_cache.get(c_type, []):
                all_local_ids.add(item['id'])
        is_monet_active = self.kernel.is_monetization_active() # (PENAMBAHAN) Cek status monetisasi
        for component in sorted(data, key=lambda x: x.get('name', '').lower()):
            searchable_string = (f"{component.get('name', '').lower()} {component.get('id', '').lower()} {component.get('description', '').lower()}")
            if all(keyword in searchable_string for keyword in search_keywords):
                status = ""
                if is_local_tab:
                    status = self.loc.get('status_disabled') if component.get('is_paused') else self.loc.get('status_enabled')
                else:
                    if component.get('id') in all_local_ids:
                        status = self.loc.get('marketplace_status_installed', fallback="Installed")
                    else:
                        status = self.loc.get('marketplace_status_not_installed', fallback="Not Installed")
                tags = ('paused',) if component.get('is_paused') and is_local_tab else ('enabled',)
                values = [
                    component.get('name', ''),
                    component.get('description', '')
                ]
                if is_monet_active:
                    values.append(component.get('tier', 'N/A').capitalize())
                if component_type == 'ai_models':
                    values.append(component.get('downloads', 0))
                else:
                    values.append(component.get('version', ''))
                values.append(status)
                tree.insert("", "end", iid=component['id'], values=tuple(values), tags=tags)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {}
        tree.tag_configure('paused', foreground='grey')
        tree.tag_configure('enabled', foreground=colors.get('fg', 'white'))
    def _on_search(self, *args):
        if not self.ui_ready: return
        self._refresh_all_lists()
    def _on_tab_change(self, event=None):
        self._update_button_state()
        self._refresh_all_lists()
    def _update_button_state(self, event=None):
        if not self.ui_ready or not self.winfo_exists():
            return
        comp_type, tree, is_local = self._get_current_tab_info()
        if not tree or not tree.winfo_exists():
            return
        selected_items = tree.selection()
        all_buttons_exist = all(hasattr(self, btn) and getattr(self, btn).winfo_exists() for btn in ['install_button', 'toggle_button', 'uninstall_button', 'upload_button'])
        if not all_buttons_exist:
            return
        if is_local:
            self.install_button.config(text=self.loc.get('marketplace_install_btn', fallback="Install from Zip..."), state="normal")
            self.toggle_button.config(state="disabled", text=self.loc.get('marketplace_disable_btn', fallback="Disable Selected"))
            self.uninstall_button.config(state="disabled")
            self.upload_button.config(state="disabled")
            if not selected_items: return
            selected_id = selected_items[0]
            component_data = next((item for item in self.local_cache.get(comp_type, []) if item['id'] == selected_id), None)
            if not component_data: return
            is_core = component_data.get('is_core', False)
            if not is_core:
                self.uninstall_button.config(state="normal")
                can_upload = self.kernel.current_user is not None
                self.upload_button.config(state="normal" if can_upload else "disabled")
                is_preset = comp_type == 'presets'
                is_model = comp_type == 'ai_models'
                self.toggle_button.config(state="normal" if not is_preset and not is_model else "disabled")
                tags = tree.item(selected_id, "tags")
                if 'paused' in tags:
                    self.toggle_button.config(text=self.loc.get('marketplace_enable_btn', fallback="Enable Selected"))
                else:
                    self.toggle_button.config(text=self.loc.get('marketplace_disable_btn', fallback="Disable Selected"))
        else: # Community tab
            install_text = self.loc.get('marketplace_install_model_btn', fallback="Download Model") if comp_type == 'ai_models' else self.loc.get('marketplace_install_community_btn', fallback="Install from Community")
            self.install_button.config(text=install_text, state="normal" if selected_items else "disabled")
            self.toggle_button.config(state="disabled")
            self.uninstall_button.config(state="disabled")
            self.upload_button.config(state="disabled")
    def _upload_selected_component(self):
        if not self.kernel.current_user:
            messagebox.showwarning("Login Required", "You must be logged in to upload components to the marketplace.", parent=self)
            if hasattr(self.kernel.root, '_open_authentication_dialog'):
                self.kernel.root._open_authentication_dialog()
            return
        comp_type, tree, is_local = self._get_current_tab_info()
        if not is_local or not tree: return
        selected_items = tree.selection()
        if not selected_items: return
        component_id = selected_items[0]
        component_name = tree.item(component_id, "values")[0]
        dialog = UploadDialog(self, self.kernel, component_name)
        if not dialog.result:
            self.kernel.write_to_log("Upload process cancelled by user.", "INFO")
            return
        upload_details = dialog.result
        if not messagebox.askyesno(
            self.loc.get('marketplace_upload_confirm_title'),
            self.loc.get('marketplace_upload_confirm_message', component_name=component_name)
        ):
            return
        self.kernel.write_to_log(f"UI: Sending upload request for '{component_name}' to the API server...", "INFO")
        if comp_type == 'ai_models':
            model_path = os.path.join(self.kernel.project_root_path, "ai_models", f"{component_id}.gguf")
            threading.Thread(target=self._upload_model_worker, args=(model_path, upload_details), daemon=True).start()
        else:
            threading.Thread(target=self._upload_worker, args=(comp_type, component_id, upload_details), daemon=True).start()
    def _upload_model_worker(self, model_path, upload_details):
        self.after(0, self.upload_button.config, {"state": "disabled", "text": "Uploading Model..."})
        success, response = self.api_client.upload_model(
            model_path=model_path,
            description=upload_details['description'],
            tier=upload_details['tier']
        )
        if success:
            self.after(0, messagebox.showinfo, self.loc.get('messagebox_success_title'), self.loc.get('marketplace_upload_success'))
        else:
            error_message = response if isinstance(response, str) else response.get('error', 'Unknown error occurred.')
            self.after(0, messagebox.showerror, self.loc.get('messagebox_error_title'), self.loc.get('marketplace_upload_failed', error=error_message))
        self.after(0, self.upload_button.config, {"state": "normal", "text": self.loc.get('marketplace_upload_btn')})
        self.after(0, self._fetch_all_data_and_refresh)
    def _upload_worker(self, comp_type, component_id, upload_details):
        self.after(0, self.upload_button.config, {"state": "disabled", "text": "Uploading..."})
        success, response = self.api_client.upload_component(
            comp_type=comp_type,
            component_id=component_id,
            description=upload_details['description'],
            tier=upload_details['tier']
        )
        if success:
            self.after(0, messagebox.showinfo, self.loc.get('messagebox_success_title'), self.loc.get('marketplace_upload_success'))
        else:
            error_message = response if isinstance(response, str) else response.get('error', 'Unknown error occurred.')
            self.after(0, messagebox.showerror, self.loc.get('messagebox_error_title'), self.loc.get('marketplace_upload_failed', error=error_message))
        self.after(0, self.upload_button.config, {"state": "normal", "text": self.loc.get('marketplace_upload_btn')})
        self.after(0, self._fetch_all_data_and_refresh)
    def _toggle_selected_component(self):
        comp_type, tree, is_local = self._get_current_tab_info()
        if not is_local or not tree: return
        selected_items = tree.selection()
        if not selected_items: return
        component_id = selected_items[0]
        tags = tree.item(component_id, "tags")
        is_currently_paused = 'paused' in tags
        new_paused_state = not is_currently_paused
        success, response = self.api_client.update_component_state(comp_type, component_id, new_paused_state)
        if success:
            action = "disabled" if new_paused_state else "enabled"
            self.kernel.write_to_log(f"Component '{component_id}' has been {action}.", "SUCCESS")
            if messagebox.askyesno(
                self.loc.get('marketplace_hot_reload_prompt_title', fallback="Reload Required"),
                self.loc.get('marketplace_toggle_hot_reload_prompt_message', fallback="State changed successfully. Reload all components now to apply?")
            ):
                threading.Thread(target=self.api_client.trigger_hot_reload, daemon=True).start()
        else:
            messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")
    def _uninstall_selected_component(self):
        comp_type, tree, is_local = self._get_current_tab_info()
        if not is_local or not tree: return
        selected_items = tree.selection()
        if not selected_items: return
        component_id = selected_items[0]
        component_name = tree.item(component_id, "values")[0]
        if not messagebox.askyesno(self.loc.get('messagebox_confirm_title'), self.loc.get('marketplace_uninstall_confirm', component_name=component_name)):
            return
        success, response = self.api_client.delete_component(comp_type, component_id)
        if success:
            self.kernel.write_to_log(f"Component '{component_id}' has been uninstalled.", "SUCCESS")
            if messagebox.askyesno(
                self.loc.get('marketplace_hot_reload_prompt_title', fallback="Reload Required"),
                self.loc.get('marketplace_uninstall_hot_reload_prompt_message', fallback="Uninstallation successful. Reload all components now to apply changes?")
            ):
                threading.Thread(target=self.api_client.trigger_hot_reload, daemon=True).start()
        else:
            messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")
    def _install_component(self):
        comp_type, tree, is_local = self._get_current_tab_info()
        if not is_local: # Community Tab Logic
            if not self.kernel.is_monetization_active():
                if not self.kernel.current_user:
                    messagebox.showwarning("Login Required", "You must be logged in to download components from the community.", parent=self)
                    if hasattr(self.kernel.root, '_open_authentication_dialog'):
                        self.kernel.root._open_authentication_dialog()
                    return # Hentikan proses install
            if not tree: return
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showwarning(
                    self.loc.get('marketplace_warn_no_selection_title', fallback="Warning"),
                    self.loc.get('marketplace_warn_no_selection_msg', fallback="Please select a component from the community list to install.")
                )
                return
            component_id = selected_items[0]
            component_data = next((item for item in self.community_cache.get(comp_type, []) if item['id'] == component_id), None)
            if not component_data: return
            required_tier = component_data.get('tier', 'free').lower()
            if not self.kernel.is_tier_sufficient(required_tier):
                messagebox.showerror(
                    self.loc.get('marketplace_install_failed_title', fallback="Installation Failed"),
                    self.loc.get('marketplace_install_tier_error', tier=required_tier.capitalize(), userTier=self.kernel.license_tier.capitalize(), fallback=f"This component requires a '{required_tier.capitalize()}' tier license, but your current tier is '{self.kernel.license_tier.capitalize()}'.")
                )
                return
            if comp_type == 'presets':
                threading.Thread(target=self._download_and_install_preset_worker, args=(component_data,), daemon=True).start()
                return
            if comp_type == 'ai_models':
                threading.Thread(target=self._download_and_install_model_worker, args=(component_data,), daemon=True).start()
                return
            download_url = component_data.get('download_url')
            if not download_url:
                messagebox.showerror(self.loc.get('error_title', fallback="Error"), self.loc.get('marketplace_install_no_url_error', fallback="The download URL for this component is not available."))
                return
            threading.Thread(target=self._download_and_install_worker, args=(comp_type, component_data), daemon=True).start()
        else: # Local Tab Logic
            filepath = filedialog.askopenfilename(
                title=self.loc.get('marketplace_install_dialog_title'),
                filetypes=[("Zip files", "*.zip")]
            )
            if not filepath:
                return
            success, response = self.api_client.install_component(comp_type, filepath)
            self._on_install_complete(success, response)
    def _download_and_install_model_worker(self, model_data):
        download_url = model_data.get('download_url')
        model_name = model_data.get('id')
        self.after(0, self.install_button.config, {"state": "disabled", "text": f"Downloading {model_name}..."})
        try:
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                save_path = os.path.join(self.kernel.project_root_path, "ai_models", f"{model_name}.gguf")
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            self.api_client.trigger_hot_reload()
            self.after(0, messagebox.showinfo, self.loc.get('messagebox_success_title'), f"Model '{model_name}' downloaded successfully to your ai_models folder.")
            self.after(0, self._fetch_all_data_and_refresh)
        except Exception as e:
            self.after(0, messagebox.showerror, self.loc.get('messagebox_error_title'), f"Failed to download model: {e}")
        finally:
            self.after(0, self.install_button.config, {"state": "normal", "text": self.loc.get('marketplace_install_model_btn')})
    def _download_and_install_preset_worker(self, preset_data):
        download_url = preset_data.get('download_url')
        preset_name = preset_data.get('id')
        self.after(0, self.install_button.config, {"state": "disabled", "text": f"Downloading {preset_name}..."})
        try:
            response = requests.get(download_url, timeout=20)
            response.raise_for_status()
            preset_content = response.json()
            success, save_response = self.api_client.save_preset(preset_name, preset_content)
            if success:
                self.after(0, messagebox.showinfo, self.loc.get('messagebox_success_title'), f"Preset '{preset_name}' was installed successfully.")
                self.after(0, self._fetch_all_data_and_refresh)
            else:
                self.after(0, messagebox.showerror, self.loc.get('messagebox_error_title'), f"Failed to save preset: {save_response}")
        except requests.exceptions.RequestException as e:
            self.after(0, messagebox.showerror, self.loc.get('messagebox_error_title'), f"Failed to download preset: {e}")
        except json.JSONDecodeError:
            self.after(0, messagebox.showerror, self.loc.get('messagebox_error_title'), "Downloaded preset file is not valid JSON.")
        except Exception as e:
            self.after(0, messagebox.showerror, self.loc.get('messagebox_error_title'), f"An unexpected error occurred: {e}")
        finally:
            self.after(0, self.install_button.config, {"state": "normal", "text": "Install Pilihan dari Komunitas"})
    def _download_and_install_worker(self, comp_type, component_data):
        download_url = component_data.get('download_url')
        component_name = component_data.get('name')
        self.after(0, self.install_button.config, {"state": "disabled", "text": f"Downloading {component_name}..."})
        try:
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
                    temp_filepath = tmp_file.name
                    for chunk in r.iter_content(chunk_size=8192):
                        tmp_file.write(chunk)
            success, response = self.api_client.install_component(comp_type, temp_filepath)
            os.unlink(temp_filepath)
            self.after(0, self._on_install_complete, success, response)
        except Exception as e:
            self.after(0, self._on_install_complete, False, str(e))
    def _on_install_complete(self, success, response):
        if success:
            self.kernel.write_to_log(f"Component installed via community tab.", "SUCCESS")
            if messagebox.askyesno(
                self.loc.get('marketplace_hot_reload_prompt_title', fallback="Reload Required"),
                self.loc.get('marketplace_install_hot_reload_prompt_message', fallback="Installation successful. Reload all components now to use the new component?")
            ):
                threading.Thread(target=self.api_client.trigger_hot_reload, daemon=True).start()
        else:
            messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")
        self._update_button_state()
