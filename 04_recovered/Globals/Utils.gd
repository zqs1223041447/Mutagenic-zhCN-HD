extends Node

const prefixes = ["", "K", "M", "B", "T", "q", "Q", "s", "S", "O", "N"]

func get_sign(number):
				if number > 0:
								return "+"
				return ""

func render_suffix_number(number):
				if number == 0:
								return "0"
				var digits = ceil(log(ceil(number)) / log(10))

				if digits < 3:
								return "%d" % number

				var prefix_amount = floor((digits - 1) / 3)
				var prefix = prefixes[prefix_amount]
				var sig_num = floor(number / pow(10, prefix_amount * 3))
				var dec_num = str(floor(number - sig_num * pow(10, prefix_amount * 3))).substr(0, 2)
				return "%d.%s%s" % [sig_num, dec_num, prefix]

func render_time(time):
				var seconds = time % 60
				var minutes = floor(time / 60)
				var label = "%02d:%02d" % [minutes, seconds]
				return label
