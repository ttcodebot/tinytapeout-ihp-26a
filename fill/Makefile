SRC = ../foundry_submission/gds/tt_ihp_wrapper.gds
FINAL_GDS = ../foundry_submission/gds/tt_ihp_wrapper_final.gds
TMP_DIR = tmp
KLAYOUT_CMD ?= klayout
SYSTEM_PYTHON ?= python3

.PHONY: all clean fill

all: fill

fill: $(FINAL_GDS)

$(TMP_DIR):
	mkdir -p $(TMP_DIR)

# Step 1: Simplify + KLayout FEOL fill
$(TMP_DIR)/step-simplify.gds: $(SRC) | $(TMP_DIR)
	$(SYSTEM_PYTHON) ./ihp_fill_simplify.py $< $@

$(TMP_DIR)/step-feol.gds: $(TMP_DIR)/step-simplify.gds | $(TMP_DIR)
	$(KLAYOUT_CMD) -b -zz \
		-r ${PDK_ROOT}/${PDK}/libs.tech/klayout/tech/scripts/filler.py \
		-rd output_file=$@ \
		-rd no_metal \
		-rd no_topmetal \
		$<

# Step 2: KLayout BEOL fill + M2 boost
$(TMP_DIR)/step-metal.gds: $(SRC) | $(TMP_DIR)
	$(KLAYOUT_CMD) -b -zz \
		-r ${PDK_ROOT}/${PDK}/libs.tech/klayout/tech/scripts/filler.py \
		-rd output_file=$@ \
		-rd no_activ \
		$<

$(TMP_DIR)/step-metal-boost.gds: $(TMP_DIR)/step-metal.gds | $(TMP_DIR)
	$(KLAYOUT_CMD) -b -zz \
		-r ./ihp_fill_m2_boost.lym \
		-rd output_file=$@ \
		$<

# Step 3: Combine KLayout metal + FEOL
$(TMP_DIR)/step-klayout.gds: $(TMP_DIR)/step-metal-boost.gds $(TMP_DIR)/step-feol.gds | $(TMP_DIR)
	$(SYSTEM_PYTHON) ./ihp_fill_combine.py $^ $@

# Step 4: Magic BEOL fill
$(TMP_DIR)/step-magic.gds: $(SRC) | $(TMP_DIR)
	cp $(abspath $<) $(TMP_DIR)/tt_ihp_wrapper.gds
	cd $(TMP_DIR) && python3 ${PDK_ROOT}/${PDK}/libs.tech/magic/generate_fill.py \
		tt_ihp_wrapper.gds -dist
	$(SYSTEM_PYTHON) ./ihp_magic_fill_collect.py $(TMP_DIR) $@

# Step 5: Replace KLayout M2/M3 fill with Magic M2/M3
$(FINAL_GDS): $(TMP_DIR)/step-klayout.gds $(TMP_DIR)/step-magic.gds
	$(SYSTEM_PYTHON) ./ihp_fill_merge.py $^ $@

clean:
	rm -rf $(TMP_DIR) $(FINAL_GDS)
