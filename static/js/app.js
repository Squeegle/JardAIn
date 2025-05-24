// JardAIn Garden Planner - Frontend JavaScript

class GardenPlannerApp {
    constructor() {
        this.selectedPlants = new Set();
        this.availablePlants = [];
        this.searchResults = [];
        this.searchTimeout = null;
        this.isSearching = false;
        this.init();
    }

    async init() {
        console.log('🌱 Initializing JardAIn Garden Planner...');
        
        // Load available plants
        await this.loadPlants();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('✅ App initialized successfully!');
    }

    async loadPlants() {
        try {
            const response = await fetch('/api/plants');
            const data = await response.json();
            this.availablePlants = data.plants || [];
            this.renderPlantGrid();
        } catch (error) {
            console.error('Error loading plants:', error);
            this.showError('Failed to load plant database. Please refresh the page.');
        }
    }

    renderPlantGrid() {
        const plantGrid = document.getElementById('plant-grid');
        if (!plantGrid) {
            console.warn('Plant grid element not found');
            return;
        }

        plantGrid.innerHTML = this.availablePlants.map(plant => `
            <div class="plant-card" data-plant="${plant.name}" onclick="app.togglePlant('${plant.name}')">
                <div class="plant-emoji">${this.getPlantEmoji(plant.type)}</div>
                <div class="plant-name">${plant.name}</div>
                <div class="plant-type">${plant.type}</div>
            </div>
        `).join('');
        
        console.log(`✅ Loaded ${this.availablePlants.length} plants`);
    }

    getPlantEmoji(type) {
        const emojis = {
            'fruit': '🍅',
            'leafy_green': '🥬',
            'root_vegetable': '🥕',
            'herb': '🌿',
            'legume': '🌱',
            'vine': '🥒',
            'bulb': '🧅',
            'cruciferous': '🥦'
        };
        return emojis[type] || '🌱';
    }

    togglePlant(plantName) {
        if (this.selectedPlants.has(plantName)) {
            this.selectedPlants.delete(plantName);
        } else {
            this.selectedPlants.add(plantName);
        }
        
        // Update visual selection
        const plantCard = document.querySelector(`[data-plant="${plantName}"]`);
        if (plantCard) {
            plantCard.classList.toggle('selected');
        }
        
        // Update selected count
        this.updateSelectedCount();
        
        console.log(`Selected plants: ${Array.from(this.selectedPlants).join(', ')}`);
    }

    updateSelectedCount() {
        const countElement = document.getElementById('selected-count');
        if (countElement) {
            countElement.textContent = this.selectedPlants.size;
        }
        
        // Enable/disable generate button
        const generateBtn = document.getElementById('generate-btn');
        if (generateBtn) {
            generateBtn.disabled = this.selectedPlants.size === 0;
        }
    }

    setupEventListeners() {
        // Generate plan button
        const generateBtn = document.getElementById('generate-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generateGardenPlan());
        }

        // Enhanced plant search with AI integration
        const searchInput = document.getElementById('plant-search');
        if (searchInput) {
            // Real-time search with debouncing
            searchInput.addEventListener('input', (e) => this.handleSearchInput(e.target.value));
            
            // Handle autocomplete selection
            searchInput.addEventListener('keydown', (e) => this.handleSearchKeydown(e));
            
            // Close autocomplete when clicking outside
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.plant-search')) {
                    this.hideAutocomplete();
                }
            });
        }
    }

    // ========================
    // Enhanced Search Methods
    // ========================
    
    handleSearchInput(searchTerm) {
        // Clear existing timeout
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        // If empty search, show all plants and hide autocomplete
        if (!searchTerm.trim()) {
            this.showAllPlants();
            this.hideAutocomplete();
            return;
        }
        
        // Debounce search to avoid excessive API calls
        this.searchTimeout = setTimeout(() => {
            this.performSearch(searchTerm);
        }, 300);
    }
    
    async performSearch(searchTerm) {
        console.log(`🔍 Searching for: "${searchTerm}"`);
        
        this.isSearching = true;
        this.showSearching();
        
        try {
            // First, filter existing static plants for immediate feedback
            this.filterStaticPlants(searchTerm);
            
            // Then, search via API (including potential AI generation)
            const response = await fetch(`/api/plants/search?q=${encodeURIComponent(searchTerm)}&include_generated=false`);
            
            if (!response.ok) {
                throw new Error(`Search failed: ${response.status}`);
            }
            
            const searchResults = await response.json();
            this.displaySearchResults(searchResults, searchTerm);
            
        } catch (error) {
            console.error('Search error:', error);
            this.showSearchError(searchTerm);
        } finally {
            this.isSearching = false;
            this.hideSearching();
        }
    }
    
    filterStaticPlants(searchTerm) {
        const plantCards = document.querySelectorAll('.plant-card');
        const query = searchTerm.toLowerCase();
        
        plantCards.forEach(card => {
            const plantName = card.querySelector('.plant-name').textContent.toLowerCase();
            const plantType = card.querySelector('.plant-type').textContent.toLowerCase();
            
            // Match by name or type
            const matches = plantName.includes(query) || plantType.includes(query);
            card.style.display = matches ? 'block' : 'none';
        });
    }
    
    displaySearchResults(searchResults, originalQuery) {
        const { plants, total_results } = searchResults;
        
        // Show autocomplete dropdown with results
        this.showAutocomplete(plants, originalQuery, total_results);
        
        // If we have results, also filter the main grid
        if (plants.length > 0) {
            this.highlightSearchResults(plants);
        }
    }
    
    showAutocomplete(plants, query, totalResults) {
        // Create or get autocomplete container
        let autocomplete = document.getElementById('search-autocomplete');
        if (!autocomplete) {
            autocomplete = this.createAutocompleteContainer();
        }
        
        // Build autocomplete content
        let content = '';
        
        // Show found plants
        if (plants.length > 0) {
            content += '<div class="autocomplete-section">';
            content += '<div class="autocomplete-header">Found Plants</div>';
            
            plants.forEach(plant => {
                const isStatic = this.availablePlants.some(p => p.name === plant.name);
                const badge = isStatic ? '<span class="plant-badge static">In Garden</span>' : '<span class="plant-badge ai">AI Generated</span>';
                
                content += `
                    <div class="autocomplete-item" onclick="app.selectPlantFromAutocomplete('${plant.name}')">
                        <div class="autocomplete-plant-info">
                            <span class="autocomplete-plant-name">${plant.name}</span>
                            <span class="autocomplete-plant-type">${plant.plant_type}</span>
                        </div>
                        ${badge}
                    </div>
                `;
            });
            content += '</div>';
        }
        
        // Show AI search option if no results
        if (plants.length === 0) {
            content += `
                <div class="autocomplete-section">
                    <div class="autocomplete-header">No plants found</div>
                    <div class="autocomplete-ai-option" onclick="app.searchWithAI('${query}')">
                        <div class="ai-search-content">
                            <span class="ai-icon">🤖</span>
                            <div class="ai-search-text">
                                <div class="ai-search-title">Search with AI</div>
                                <div class="ai-search-subtitle">Discover "${query}" using artificial intelligence</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        autocomplete.innerHTML = content;
        autocomplete.style.display = 'block';
    }
    
    createAutocompleteContainer() {
        const searchContainer = document.querySelector('.plant-search');
        const autocomplete = document.createElement('div');
        autocomplete.id = 'search-autocomplete';
        autocomplete.className = 'search-autocomplete';
        searchContainer.appendChild(autocomplete);
        return autocomplete;
    }
    
    async searchWithAI(query) {
        console.log(`🤖 Searching with AI for: "${query}"`);
        
        this.hideAutocomplete();
        this.showAISearching(query);
        
        try {
            // Search with AI generation enabled
            const response = await fetch(`/api/plants/search?q=${encodeURIComponent(query)}&include_generated=true`);
            
            if (!response.ok) {
                throw new Error(`AI search failed: ${response.status}`);
            }
            
            const searchResults = await response.json();
            
            if (searchResults.plants.length > 0) {
                const newPlant = searchResults.plants[0];
                this.addAIPlantToGrid(newPlant);
                this.showSuccessMessage(`✅ Found "${newPlant.name}" using AI! Added to your plant options.`);
            } else {
                this.showErrorMessage(`❌ AI couldn't find information about "${query}". Try a different plant name.`);
            }
            
        } catch (error) {
            console.error('AI search error:', error);
            this.showErrorMessage(`❌ AI search failed: ${error.message}`);
        } finally {
            this.hideAISearching();
        }
    }
    
    addAIPlantToGrid(plant) {
        // Ensure consistent plant name
        const plantName = plant.name.trim();
        
        // Add to available plants array  
        this.availablePlants.push(plant);
        
        // Create new plant card with AI badge
        const plantGrid = document.getElementById('plant-grid');
        const plantCard = document.createElement('div');
        plantCard.className = 'plant-card ai-generated';
        plantCard.setAttribute('data-plant', plantName);
        plantCard.onclick = () => this.togglePlant(plantName);
        
        plantCard.innerHTML = `
            <div class="plant-emoji">${this.getPlantEmoji(plant.plant_type)}</div>
            <div class="plant-name">${plantName}</div>
            <div class="plant-type">${plant.plant_type}</div>
            <div class="plant-badge ai">AI Generated</div>
        `;
        
        // Add to the beginning of the grid
        plantGrid.insertBefore(plantCard, plantGrid.firstChild);
        
        // Auto-select the new plant for user convenience
        this.togglePlant(plantName);
        
        // Highlight the new plant
        setTimeout(() => {
            plantCard.classList.add('newly-added');
            setTimeout(() => plantCard.classList.remove('newly-added'), 2000);
        }, 100);
        
        console.log(`✅ Added AI plant "${plantName}" to grid and selected it`);
    }
    
    selectPlantFromAutocomplete(plantName) {
        // If plant is already in grid, just select it
        const existingCard = document.querySelector(`[data-plant="${plantName}"]`);
        if (existingCard) {
            this.togglePlant(plantName);
            this.hideAutocomplete();
            return;
        }
        
        // If it's an AI plant not in grid, add it
        this.hideAutocomplete();
        this.showInfoMessage(`Adding "${plantName}" to your plant options...`);
        
        // We'll need to fetch the full plant info and add it
        this.fetchAndAddPlant(plantName);
    }
    
    async fetchAndAddPlant(plantName) {
        try {
            const response = await fetch(`/api/plants/${encodeURIComponent(plantName)}`);
            if (!response.ok) {
                throw new Error(`Failed to fetch plant: ${response.status}`);
            }
            
            const plant = await response.json();
            this.addAIPlantToGrid(plant);
            this.togglePlant(plantName); // Auto-select it
            
        } catch (error) {
            console.error('Error fetching plant:', error);
            this.showErrorMessage(`Failed to add "${plantName}": ${error.message}`);
        }
    }
    
    // Utility methods for search UI
    showAllPlants() {
        const plantCards = document.querySelectorAll('.plant-card');
        plantCards.forEach(card => {
            card.style.display = 'block';
        });
    }
    
    hideAutocomplete() {
        const autocomplete = document.getElementById('search-autocomplete');
        if (autocomplete) {
            autocomplete.style.display = 'none';
        }
    }
    
    showSearching() {
        // Could add a subtle loading indicator to search box
        const searchInput = document.getElementById('plant-search');
        if (searchInput) {
            searchInput.classList.add('searching');
        }
    }
    
    hideSearching() {
        const searchInput = document.getElementById('plant-search');
        if (searchInput) {
            searchInput.classList.remove('searching');
        }
    }
    
    showAISearching(query) {
        this.showInfoMessage(`🤖 AI is analyzing "${query}"... This may take a moment.`);
    }
    
    hideAISearching() {
        // Message will auto-hide
    }
    
    handleSearchKeydown(e) {
        // Handle Enter key, arrow keys for autocomplete navigation
        if (e.key === 'Enter') {
            e.preventDefault();
            // Could select first autocomplete item
        } else if (e.key === 'Escape') {
            this.hideAutocomplete();
        }
    }
    
    highlightSearchResults(plants) {
        // Visual feedback for which plants match search
        const plantCards = document.querySelectorAll('.plant-card');
        plantCards.forEach(card => {
            card.classList.remove('search-match');
        });
        
        plants.forEach(plant => {
            const card = document.querySelector(`[data-plant="${plant.name}"]`);
            if (card) {
                card.classList.add('search-match');
            }
        });
    }
    
    showSearchError(query) {
        this.showErrorMessage(`Search failed for "${query}". Please try again.`);
    }
    
    // Message utility methods
    showInfoMessage(message) {
        this.showMessage(message, 'info');
    }
    
    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }
    
    showErrorMessage(message) {
        this.showMessage(message, 'error');
    }
    
    showMessage(message, type = 'info') {
        // Create or get message container
        let messageContainer = document.getElementById('message-container');
        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.id = 'message-container';
            messageContainer.className = 'message-container';
            document.body.appendChild(messageContainer);
        }
        
        // Create message element
        const messageElement = document.createElement('div');
        messageElement.className = `message message-${type}`;
        messageElement.textContent = message;
        
        // Add to container
        messageContainer.appendChild(messageElement);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.parentNode.removeChild(messageElement);
            }
        }, 5000);
    }

    async generateGardenPlan() {
        const zipCode = document.getElementById('zip-code').value;
        const gardenSize = document.getElementById('garden-size').value;
        
        if (!zipCode) {
            this.showError('Please enter your zip code.');
            return;
        }
        
        if (this.selectedPlants.size === 0) {
            this.showError('Please select at least one plant.');
            return;
        }

        // Show loading state
        this.showLoading();

        try {
            const requestData = {
                zip_code: zipCode,
                selected_plants: Array.from(this.selectedPlants),
                garden_size: gardenSize || 'medium',
                experience_level: 'beginner'
            };

            console.log('🚀 Generating garden plan:', requestData);
            console.log('🔍 Selected plants debug:', Array.from(this.selectedPlants));
            console.log('🔍 Available plants in frontend:', this.availablePlants.map(p => p.name));

            const response = await fetch('/api/plans', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const gardenPlan = await response.json();
            console.log('✅ Garden plan generated:', gardenPlan);
            console.log('🔍 Plants in plan:', gardenPlan.plant_information?.map(p => p.name) || 'No plant info');
            
            // Complete the loading animation with celebration
            this.finalizeLoading();
            
            // Wait a moment for the completion animation to be visible
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            this.displayResults(gardenPlan);
            
            // Generate PDF option
            this.showPDFOption(gardenPlan.plan_id);

        } catch (error) {
            console.error('Error generating garden plan:', error);
            this.showError(`Failed to generate garden plan: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    displayResults(gardenPlan) {
        // Store for debugging
        this.lastGeneratedPlan = gardenPlan;
        
        const resultsDiv = document.getElementById('results');
        if (!resultsDiv) return;

        // Show only a minimal success message
        resultsDiv.innerHTML = `
            <div class="alert alert-success">
                <strong>✅ Garden Plan Generated Successfully!</strong><br>
                Your personalized plan for ${gardenPlan.location.city}, ${gardenPlan.location.state} 
                (Zone ${gardenPlan.location.usda_zone}) is ready.<br>
                <small>📱 ${gardenPlan.plant_information.length} plants included • Generated ${new Date().toLocaleDateString()}</small>
            </div>
        `;

        resultsDiv.style.display = 'block';
        
        // Don't scroll to results - let user naturally see the download button
    }

    renderPlantingSchedule(schedules) {
        console.log('🔍 Rendering planting schedules:', schedules);
        
        if (!schedules || !Array.isArray(schedules) || schedules.length === 0) {
            return '<div class="plan-section"><h3>📅 Planting Schedule</h3><p>No planting schedule available.</p></div>';
        }

        return `
            <div class="plan-section">
                <h3>📅 Planting Schedule</h3>
                <div class="schedule-grid">
                    ${schedules.map(schedule => `
                        <div class="schedule-item">
                            <h4>${schedule.plant_name}</h4>
                            ${schedule.start_indoors_date ? `<p><strong>Start Indoors:</strong> ${schedule.start_indoors_date}</p>` : ''}
                            ${schedule.direct_sow_date ? `<p><strong>Direct Sow:</strong> ${schedule.direct_sow_date}</p>` : ''}
                            ${schedule.transplant_date ? `<p><strong>Transplant:</strong> ${schedule.transplant_date}</p>` : ''}
                            ${schedule.harvest_start_date ? `<p><strong>Harvest Start:</strong> ${schedule.harvest_start_date}</p>` : ''}
                            ${schedule.harvest_end_date ? `<p><strong>Harvest End:</strong> ${schedule.harvest_end_date}</p>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderGrowingInstructions(instructions) {
        console.log('🔍 Rendering growing instructions:', instructions);
        
        if (!instructions || !Array.isArray(instructions) || instructions.length === 0) {
            return '<div class="plan-section"><h3>🌱 Growing Instructions</h3><p>No growing instructions available.</p></div>';
        }

        return `
            <div class="plan-section">
                <h3>🌱 Growing Instructions</h3>
                <div class="instructions-list">
                    ${instructions.map(instruction => `
                        <div class="instruction-item">
                            <h4>${instruction.plant_name}</h4>
                            
                            ${instruction.preparation_steps && instruction.preparation_steps.length > 0 ? `
                                <div class="instruction-section">
                                    <h5>🏗️ Preparation Steps</h5>
                                    <ul>
                                        ${instruction.preparation_steps.map(step => `<li>${step}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                            
                            ${instruction.planting_steps && instruction.planting_steps.length > 0 ? `
                                <div class="instruction-section">
                                    <h5>🌱 Planting Steps</h5>
                                    <ul>
                                        ${instruction.planting_steps.map(step => `<li>${step}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                            
                            ${instruction.care_instructions && instruction.care_instructions.length > 0 ? `
                                <div class="instruction-section">
                                    <h5>🌿 Care Instructions</h5>
                                    <ul>
                                        ${instruction.care_instructions.map(step => `<li>${step}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderGeneralTips(tips) {
        if (!tips || !Array.isArray(tips) || tips.length === 0) {
            return '';
        }

        return `
            <div class="plan-section">
                <h3>💡 General Tips</h3>
                <ul>
                    ${tips.map(tip => `<li>${tip}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    showPDFOption(planId) {
        const pdfSection = document.getElementById('pdfSection');
        if (pdfSection) {
            pdfSection.innerHTML = `
                <div class="pdf-download-container" style="text-align: center; margin: 2rem 0; padding: 2rem; background: #f8fffe; border-radius: 12px; border: 2px solid #4a7c59;">
                    <h3 style="color: #2d5a2d; margin-bottom: 1rem;">📄 Your Garden Plan is Ready!</h3>
                    <button class="btn btn-pdf-download" onclick="app.downloadPDF('${planId}')" 
                            style="background: #4a7c59; color: white; border: none; padding: 1rem 2rem; font-size: 1.1rem; border-radius: 8px; cursor: pointer; transition: all 0.3s ease;">
                        📥 Download PDF Garden Plan
                    </button>
                    <p style="margin-top: 1rem; color: #666; font-size: 0.9rem;">
                        Your complete garden plan with planting schedules, growing instructions, and layout recommendations.
                    </p>
                </div>
            `;
            pdfSection.style.display = 'block';
            
            // Add hover effect to button
            const button = pdfSection.querySelector('.btn-pdf-download');
            button.addEventListener('mouseenter', () => {
                button.style.background = '#2d5a2d';
                button.style.transform = 'translateY(-2px)';
            });
            button.addEventListener('mouseleave', () => {
                button.style.background = '#4a7c59';
                button.style.transform = 'translateY(0)';
            });
            
            // Scroll to the download section smoothly
            pdfSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    async downloadPDF(planId) {
        try {
            const response = await fetch(`/api/pdf/garden-plan/${planId}`);
            
            if (!response.ok) {
                throw new Error('Failed to generate PDF');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `garden-plan-${planId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.showSuccess('PDF downloaded successfully!');
        } catch (error) {
            console.error('Error downloading PDF:', error);
            this.showError('Failed to download PDF. Please try again.');
        }
    }

    showLoading() {
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div class="step-loading">
                    <div class="loading-container">
                        <div class="loading-header">
                            <div class="loading-icon">🌱</div>
                            <h2 class="loading-title">Creating Your Garden Plan</h2>
                        </div>
                        
                        <div class="loading-steps">
                            <div class="step-item" id="step-1">
                                <div class="step-icon">📍</div>
                                <div class="step-content">
                                    <div class="step-title">Analyzing Location</div>
                                    <div class="step-description">Getting climate data for your area</div>
                                </div>
                                <div class="step-status">⏳</div>
                            </div>
                            
                            <div class="step-item" id="step-2">
                                <div class="step-icon">🌱</div>
                                <div class="step-content">
                                    <div class="step-title">Plant Information</div>
                                    <div class="step-description">Gathering details for selected plants</div>
                                </div>
                                <div class="step-status">⏸️</div>
                            </div>
                            
                            <div class="step-item" id="step-3">
                                <div class="step-icon">📅</div>
                                <div class="step-content">
                                    <div class="step-title">Planting Schedules</div>
                                    <div class="step-description">Creating personalized timing</div>
                                </div>
                                <div class="step-status">⏸️</div>
                            </div>
                            
                            <div class="step-item" id="step-4">
                                <div class="step-icon">📋</div>
                                <div class="step-content">
                                    <div class="step-title">Growing Instructions</div>
                                    <div class="step-description">Generating care guides</div>
                                </div>
                                <div class="step-status">⏸️</div>
                            </div>
                            
                            <div class="step-item" id="step-5">
                                <div class="step-icon">📄</div>
                                <div class="step-content">
                                    <div class="step-title">Finalizing Plan</div>
                                    <div class="step-description">Putting it all together</div>
                                </div>
                                <div class="step-status">⏸️</div>
                            </div>
                        </div>
                        
                        <div class="progress-section">
                            <div class="progress-bar">
                                <div class="progress-fill" id="progress-fill"></div>
                            </div>
                            <div class="progress-text" id="progress-text">Step 1 of 5</div>
                        </div>
                    </div>
                </div>
            `;
            resultsDiv.style.display = 'block';
            
            // Start the step-based loading animation
            this.startStepLoading();
        }
    }

    hideLoading() {
        // Mark animation as completed
        this.animationCompleted = true;
        
        // Clear any running animations
        if (this.loadingInterval) {
            clearInterval(this.loadingInterval);
            this.loadingInterval = null;
        }
        if (this.stepTimeout) {
            clearTimeout(this.stepTimeout);
            this.stepTimeout = null;
        }
        
        console.log('🔄 Step loading animation stopped and cleaned up');
    }
    
    // ========================
    // Clean Loading Animation System
    // ========================
    
    startStepLoading() {
        // Initialize step-based loading state
        this.currentStep = 1;
        this.totalSteps = 5;
        this.loadingProgress = 0;
        this.startTime = Date.now();
        this.animationCompleted = false;
        
        // Calculate estimated time based on number of plants (more realistic)
        const numPlants = this.selectedPlants.size;
        const baseTime = 25000; // 25 seconds base
        const perPlantTime = 2000; // 2 seconds per plant
        this.estimatedTime = baseTime + (numPlants * perPlantTime);
        
        // Step timing configuration (in milliseconds) - slower and more realistic
        // Distribute the time more evenly across steps, with longer final steps
        const stepTime1 = Math.floor(this.estimatedTime * 0.15); // 15% - Location analysis
        const stepTime2 = Math.floor(this.estimatedTime * 0.20); // 20% - Plant info
        const stepTime3 = Math.floor(this.estimatedTime * 0.25); // 25% - Schedules (most complex)
        const stepTime4 = Math.floor(this.estimatedTime * 0.25); // 25% - Instructions (complex)
        const stepTime5 = Math.floor(this.estimatedTime * 0.15); // 15% - Finalization
        
        this.stepDurations = [stepTime1, stepTime2, stepTime3, stepTime4, stepTime5];
        
        console.log(`🕐 Loading timing: ${this.estimatedTime/1000}s total for ${numPlants} plants`);
        console.log(`📊 Step durations: ${this.stepDurations.map(d => (d/1000).toFixed(1)+'s').join(', ')}`);
        
        // Start the step animations
        this.updateStepProgress();
        this.animateSteps();
    }
    
    updateStepProgress() {
        this.loadingInterval = setInterval(() => {
            // Don't update if animation is completed
            if (this.animationCompleted) {
                return;
            }
            
            const elapsed = Date.now() - this.startTime;
            
            // Calculate progress based on current step and elapsed time within that step
            let totalProgressFromSteps = 0;
            for (let i = 0; i < this.currentStep - 1; i++) {
                totalProgressFromSteps += this.stepDurations[i];
            }
            
            // Add progress within current step
            const currentStepStart = totalProgressFromSteps;
            const currentStepDuration = this.stepDurations[this.currentStep - 1] || 5000;
            const currentStepElapsed = elapsed - currentStepStart;
            const currentStepProgress = Math.min(currentStepElapsed / currentStepDuration, 1);
            
            // Total progress percentage (cap at 90% until actual completion)
            const totalElapsedFromSteps = totalProgressFromSteps + (currentStepProgress * currentStepDuration);
            this.loadingProgress = Math.min((totalElapsedFromSteps / this.estimatedTime) * 100, 90);
            
            // Update progress bar and text
            const progressFill = document.getElementById('progress-fill');
            const progressText = document.getElementById('progress-text');
            
            if (progressFill) {
                progressFill.style.width = `${this.loadingProgress}%`;
            }
            
            if (progressText) {
                const remaining = Math.max(0, Math.ceil((this.estimatedTime - elapsed) / 1000));
                if (remaining > 0) {
                    progressText.textContent = `Step ${this.currentStep} of ${this.totalSteps} • ~${remaining}s remaining`;
                } else {
                    progressText.textContent = `Step ${this.currentStep} of ${this.totalSteps} • Almost done...`;
                }
            }
        }, 200); // Update every 200ms for smooth but not excessive updates
    }
    
    animateSteps() {
        if (this.animationCompleted) {
            return;
        }
        
        // If we've reached the final step, don't auto-advance - wait for actual completion
        if (this.currentStep > this.totalSteps) {
            console.log('🏁 All steps completed, waiting for actual request to finish...');
            return;
        }
        
        console.log(`🎬 Animating step ${this.currentStep}: ${this.getStepName(this.currentStep)}`);
        
        // Mark current step as active
        const currentStepElement = document.getElementById(`step-${this.currentStep}`);
        if (currentStepElement) {
            currentStepElement.classList.add('active');
            const statusElement = currentStepElement.querySelector('.step-status');
            if (statusElement) {
                statusElement.textContent = '⏳';
            }
        }
        
        // Mark previous steps as completed
        for (let i = 1; i < this.currentStep; i++) {
            const prevStepElement = document.getElementById(`step-${i}`);
            if (prevStepElement) {
                prevStepElement.classList.remove('active');
                prevStepElement.classList.add('completed');
                const statusElement = prevStepElement.querySelector('.step-status');
                if (statusElement) {
                    statusElement.textContent = '✅';
                }
            }
        }
        
        // Schedule next step
        const stepDuration = this.stepDurations[this.currentStep - 1] || 5000;
        this.stepTimeout = setTimeout(() => {
            if (!this.animationCompleted) {
                this.currentStep++;
                this.animateSteps();
            }
        }, stepDuration);
    }
    
    getStepName(stepNumber) {
        const stepNames = [
            'Analyzing Location',
            'Plant Information', 
            'Planting Schedules',
            'Growing Instructions',
            'Finalizing Plan'
        ];
        return stepNames[stepNumber - 1] || 'Unknown Step';
    }
    
    finalizeLoading() {
        console.log('🎉 Finalizing step loading animation...');
        
        // Mark animation as completed to stop other processes
        this.animationCompleted = true;
        
        // Mark all steps as completed
        for (let i = 1; i <= this.totalSteps; i++) {
            const stepElement = document.getElementById(`step-${i}`);
            if (stepElement) {
                stepElement.classList.remove('active');
                stepElement.classList.add('completed');
                const statusElement = stepElement.querySelector('.step-status');
                if (statusElement) {
                    statusElement.textContent = '✅';
                }
            }
        }
        
        // Complete the progress bar
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        if (progressFill) progressFill.style.width = '100%';
        if (progressText) progressText.textContent = 'Complete!';
    }

    showError(message) {
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) {
            resultsDiv.innerHTML = `
                <div class="alert alert-error">
                    <strong>Error:</strong> ${message}
                </div>
            `;
            resultsDiv.style.display = 'block';
        }
    }

    showSuccess(message) {
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) {
            const successAlert = document.createElement('div');
            successAlert.className = 'alert alert-success';
            successAlert.innerHTML = `<strong>Success:</strong> ${message}`;
            resultsDiv.insertBefore(successAlert, resultsDiv.firstChild);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new GardenPlannerApp();
}); 